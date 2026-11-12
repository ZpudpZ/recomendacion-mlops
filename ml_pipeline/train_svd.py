import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import os
import pickle
import pandas as pd
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split


def main():
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    model_path = os.path.join(artifacts_dir, "svd_model.pkl")
    metadata_path = os.path.join(artifacts_dir, "item_metadata.parquet")

    # 1. Descargar/cargar el dataset integrado ml-100k
    raw_data = Dataset.load_builtin(name="ml-100k", prompt=False)

    df_ratings = pd.DataFrame(
        raw_data.raw_ratings, columns=["user_id", "item_id", "rating", "timestamp"]
    )
    df_ratings["user_id"] = df_ratings["user_id"].astype(int)
    df_ratings["item_id"] = df_ratings["item_id"].astype(int)
    df_ratings["rating"] = df_ratings["rating"].astype(float)

    reader = Reader(rating_scale=(1.0, 5.0))
    data = Dataset.load_from_df(df_ratings[["user_id", "item_id", "rating"]], reader)

    # 2. Evaluación con partición Train/Test
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

    svd_eval = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=42)
    svd_eval.fit(trainset)
    predictions = svd_eval.test(testset)

    print("=== Métricas de Evaluación SVD ===")
    accuracy.rmse(predictions, verbose=True)
    accuracy.mae(predictions, verbose=True)

    # 3. Entrenamiento con el dataset completo para producción
    full_trainset = data.build_full_trainset()
    svd_prod = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=42)
    svd_prod.fit(full_trainset)

    with open(model_path, "wb") as f:
        pickle.dump(svd_prod, f)
    print(f"Modelo guardado en: {model_path}")

    # 4. Extraer títulos reales desde el archivo u.item en la carpeta de Surprise
    surprise_dir = os.environ.get(
        "SURPRISE_DATA_FOLDER", os.path.expanduser("~/.surprise_data")
    )
    u_item_path = os.path.join(surprise_dir, "ml-100k", "ml-100k", "u.item")

    df_items = pd.read_csv(
        u_item_path,
        sep="|",
        encoding="latin-1",
        header=None,
        usecols=[0, 1],
        names=["item_id", "title"]
    )
    df_items["item_id"] = df_items["item_id"].astype(int)

    # 5. Calcular popularidad y cruzar con los títulos reales
    item_stats = (
        df_ratings.groupby("item_id")
        .agg(rating_count=("rating", "count"), avg_rating=("rating", "mean"))
        .reset_index()
    )
    item_stats["popularity_score"] = (
        item_stats["rating_count"] * item_stats["avg_rating"]
    ).round(4)

    metadata_df = pd.merge(item_stats, df_items, on="item_id", how="left")
    metadata_df["title"] = metadata_df["title"].fillna(
        metadata_df["item_id"].apply(lambda x: f"Película #{x}")
    )

    metadata_df = metadata_df[["item_id", "title", "popularity_score"]]
    metadata_df.to_parquet(metadata_path, engine="pyarrow", index=False)
    print(f"Metadata con títulos reales guardada en: {metadata_path}")


if __name__ == "__main__":
    main()