import os

MODEL_PATH: str = os.getenv("MODEL_PATH", "/app/artifacts/svd_model.pkl")
METADATA_PATH: str = os.getenv("METADATA_PATH", "/app/artifacts/item_metadata.parquet")
ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

GENRE_POOL: list[str] = [
    "Sci-Fi / Thriller",
    "Action / Adventure",
    "Drama / Mystery",
    "Crime / Noir",
    "Fantasy / Animation",
    "Documentary / History",
    "Suspense / Psychological",
    "Comedy / Romance"
]