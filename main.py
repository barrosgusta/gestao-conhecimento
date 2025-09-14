# main.py
from typing import List, Dict, Any, Optional

import pandas as pd

from exploratoria import (
    grafico_distribuicao, grafico_categorico,
    grafico_boxplot, grafico_kde, grafico_missing, grafico_correlacao
)
from function import load_database


def load_data(path: Optional[str] = None) -> pd.DataFrame:
    """Load dataset (wrapper around load_database). If path is provided, it's forwarded."""
    if path:
        return load_database(path)
    return load_database()


def numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=["int64", "float64"]).columns.tolist()


def categorical_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=["object"]).columns.tolist()


def numeric_stats(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    s = df[col].dropna()
    desc = s.describe()
    return {
        "min": float(desc.get("min", float("nan"))),
        "max": float(desc.get("max", float("nan"))),
        "mean": float(desc.get("mean", float("nan"))),
        "median": float(s.median()) if not s.empty else None,
        "count": int(desc.get("count", 0)),
    }


def figure_for_numeric(df: pd.DataFrame, col: str, plot_type: str):
    """Return a matplotlib Figure for a numeric column and plot type."""
    if plot_type == "Histograma":
        return grafico_distribuicao(df, col)
    if plot_type == "Boxplot":
        return grafico_boxplot(df, col)
    if plot_type == "KDE":
        return grafico_kde(df, col)
    raise ValueError(f"Unknown plot type: {plot_type}")


def figure_for_categorical(df: pd.DataFrame, col: str, top_n: int = 10):
    return grafico_categorico(df, col, top_n=top_n)


def figure_missing(df: pd.DataFrame):
    return grafico_missing(df)


def figure_correlation(df: pd.DataFrame):
    return grafico_correlacao(df)


# If the module is executed directly, provide a small demo loader (non-UI)
if __name__ == "__main__":
    df = load_data()
    print("Loaded dataset with shape:", df.shape)
    print("Numeric columns:", numeric_columns(df))
    print("Categorical columns:", categorical_columns(df))
