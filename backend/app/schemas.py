from typing import List, Dict, Any
from pydantic import BaseModel, Field


class RecommendedItem(BaseModel):
    item_id: int
    title: str
    genre: str
    estimated_score: float
    popularity_score: float
    confidence_pct: float
    latent_norm: float


class RecommendationResponse(BaseModel):
    user_id: int
    is_cold_start: bool
    top_n: int
    user_interactions_count: int
    recommendations: List[RecommendedItem]


class ExperimentRequest(BaseModel):
    n_factors: int = Field(100, ge=10, le=300)
    n_epochs: int = Field(20, ge=5, le=100)
    lr_all: float = Field(0.005, ge=0.0005, le=0.05)
    reg_all: float = Field(0.02, ge=0.001, le=0.5)
    test_split: float = Field(0.2, ge=0.1, le=0.5)
    sample_fraction: float = Field(0.6, ge=0.1, le=1.0)
    update_active_model: bool = Field(True)


class ExperimentResponse(BaseModel):
    rmse: float
    mae: float
    sparsity_pct: float
    compute_time_ms: float
    train_samples: int
    test_samples: int
    n_users: int
    n_items: int
    hyperparameters: Dict[str, Any]