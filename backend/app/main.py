import os
import ssl
import time
import pickle
from contextlib import asynccontextmanager
from typing import Dict, Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split

from app.config import MODEL_PATH, METADATA_PATH, ALLOWED_ORIGINS, GENRE_POOL
from app.schemas import (
    RecommendedItem,
    RecommendationResponse,
    ExperimentRequest,
    ExperimentResponse,
)

ssl._create_default_https_context = ssl._create_unverified_context

ml_artifacts: Dict[str, Any] = {
    "model": None,
    "items_df": None,
    "ratings_df": None,
    "popular_fallback": []
}


def assign_genre(item_id: int) -> str:
    return GENRE_POOL[item_id % len(GENRE_POOL)]


def extract_ratings_df(trainset) -> pd.DataFrame:
    records = [
        (int(trainset.to_raw_uid(u)), int(trainset.to_raw_iid(i)), float(r))
        for (u, i, r) in trainset.all_ratings()
    ]
    return pd.DataFrame(records, columns=["user_id", "item_id", "rating"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(METADATA_PATH):
        print("ADVERTENCIA: Artefactos no encontrados en /app/artifacts.")
    else:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
            ml_artifacts["model"] = model

        df = pd.read_parquet(METADATA_PATH)
        if "genre" not in df.columns:
            df["genre"] = df["item_id"].apply(assign_genre)

        ml_artifacts["items_df"] = df.set_index("item_id")
        ml_artifacts["ratings_df"] = extract_ratings_df(model.trainset)

        max_pop = float(df["popularity_score"].max()) if len(df) > 0 else 1.0
        top_popular = df.sort_values(by="popularity_score", ascending=False).head(50)

        ml_artifacts["popular_fallback"] = [
            RecommendedItem(
                item_id=int(row.item_id),
                title=str(row.title),
                genre=str(row.genre),
                estimated_score=round(min(5.0, 3.5 + (float(row.popularity_score) / max_pop) * 1.5), 4),
                popularity_score=round(float(row.popularity_score), 2),
                confidence_pct=round((float(row.popularity_score) / max_pop) * 100, 1),
                latent_norm=0.0
            )
            for _, row in top_popular.iterrows()
        ]
    yield
    ml_artifacts.clear()


app = FastAPI(
    title="Enterprise SVD Collaborative Filtering API",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    ready = ml_artifacts["model"] is not None and ml_artifacts["items_df"] is not None
    return {"status": "healthy" if ready else "missing_artifacts", "model_loaded": ready}


@app.post("/experiment", response_model=ExperimentResponse)
async def run_experiment(req: ExperimentRequest):
    ratings_df: pd.DataFrame = ml_artifacts.get("ratings_df")
    if ratings_df is None or ratings_df.empty:
        raise HTTPException(status_code=503, detail="Dataset base no disponible en memoria.")

    start_time = time.perf_counter()

    working_df = (
        ratings_df.sample(frac=req.sample_fraction, random_state=42)
        if req.sample_fraction < 1.0
        else ratings_df
    )

    n_users = int(working_df["user_id"].nunique())
    n_items = int(working_df["item_id"].nunique())
    matrix_capacity = max(1, n_users * n_items)
    sparsity_pct = round((1.0 - (len(working_df) / matrix_capacity)) * 100, 2)

    reader = Reader(rating_scale=(1.0, 5.0))
    data = Dataset.load_from_df(working_df[["user_id", "item_id", "rating"]], reader)
    trainset, testset = train_test_split(data, test_size=req.test_split, random_state=42)

    svd = SVD(
        n_factors=req.n_factors,
        n_epochs=req.n_epochs,
        lr_all=req.lr_all,
        reg_all=req.reg_all,
        random_state=42
    )
    svd.fit(trainset)
    predictions = svd.test(testset)

    rmse_val = round(float(accuracy.rmse(predictions, verbose=False)), 4)
    mae_val = round(float(accuracy.mae(predictions, verbose=False)), 4)

    if req.update_active_model:
        full_data = Dataset.load_from_df(ratings_df[["user_id", "item_id", "rating"]], reader)
        full_trainset = full_data.build_full_trainset()
        prod_svd = SVD(
            n_factors=req.n_factors,
            n_epochs=req.n_epochs,
            lr_all=req.lr_all,
            reg_all=req.reg_all,
            random_state=42
        )
        prod_svd.fit(full_trainset)
        ml_artifacts["model"] = prod_svd

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return ExperimentResponse(
        rmse=rmse_val,
        mae=mae_val,
        sparsity_pct=sparsity_pct,
        compute_time_ms=elapsed_ms,
        train_samples=trainset.n_ratings,
        test_samples=len(testset),
        n_users=n_users,
        n_items=n_items,
        hyperparameters=req.model_dump()
    )


@app.get("/recommend/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int = Path(..., gt=0),
    top_n: int = Query(10, ge=1, le=50)
):
    model = ml_artifacts.get("model")
    items_df = ml_artifacts.get("items_df")

    if model is None or items_df is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado en memoria.")

    try:
        inner_uid = model.trainset.to_inner_uid(user_id)
        is_cold_start = False
    except ValueError:
        is_cold_start = True

    if is_cold_start:
        return RecommendationResponse(
            user_id=user_id,
            is_cold_start=True,
            top_n=top_n,
            user_interactions_count=0,
            recommendations=ml_artifacts["popular_fallback"][:top_n]
        )

    user_history = model.trainset.ur[inner_uid]
    interacted_inner_iids = {iid for (iid, _) in user_history}
    interacted_raw_iids = {model.trainset.to_raw_iid(iid) for iid in interacted_inner_iids}

    predictions = []
    for item_id, row in items_df.iterrows():
        if item_id not in interacted_raw_iids:
            pred = model.predict(uid=user_id, iid=item_id)
            try:
                inner_iid = model.trainset.to_inner_iid(item_id)
                latent_norm = float(np.linalg.norm(model.qi[inner_iid]))
            except ValueError:
                latent_norm = 0.0

            confidence = min(99.5, max(50.0, (pred.est / 5.0) * 100))
            predictions.append((
                int(item_id),
                str(row["title"]),
                str(row["genre"]),
                float(pred.est),
                float(row["popularity_score"]),
                confidence,
                latent_norm
            ))

    predictions.sort(key=lambda x: x[3], reverse=True)
    top_predictions = predictions[:top_n]

    formatted_recs = [
        RecommendedItem(
            item_id=item_id,
            title=title,
            genre=genre,
            estimated_score=round(score, 4),
            popularity_score=round(pop_score, 2),
            confidence_pct=round(conf, 1),
            latent_norm=round(l_norm, 4)
        )
        for item_id, title, genre, score, pop_score, conf, l_norm in top_predictions
    ]

    return RecommendationResponse(
        user_id=user_id,
        is_cold_start=False,
        top_n=top_n,
        user_interactions_count=len(user_history),
        recommendations=formatted_recs
    )