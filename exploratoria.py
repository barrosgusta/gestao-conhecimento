# exploratoria.py
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

sns.set_theme(style="whitegrid")


def grafico_distribuicao(df: pd.DataFrame, coluna: str) -> Figure:
    """Return a histogram (with KDE) figure for a numeric column."""
    fig, ax = plt.subplots()
    sns.histplot(df[coluna].dropna(), kde=True, ax=ax)
    ax.set_title(f"Distribuição de {coluna}")
    ax.set_xlabel(coluna)
    fig.tight_layout()
    return fig


def grafico_categorico(df: pd.DataFrame, coluna: str, top_n: int = 10) -> Figure:
    """Return a horizontal bar chart for the top N categories."""
    top_values = df[coluna].value_counts().head(top_n)
    fig, ax = plt.subplots()
    sns.barplot(x=top_values.values, y=top_values.index, ax=ax)
    ax.set_title(f"Top {top_n} categorias de {coluna}")
    ax.set_xlabel("Frequência")
    fig.tight_layout()
    return fig


def grafico_boxplot(df: pd.DataFrame, coluna: str) -> Figure:
    """Return a boxplot figure for a numeric column."""
    fig, ax = plt.subplots()
    sns.boxplot(x=df[coluna].dropna(), ax=ax)
    ax.set_title(f"Boxplot de {coluna}")
    fig.tight_layout()
    return fig


def grafico_kde(df: pd.DataFrame, coluna: str) -> Figure:
    """Return a KDE (density) plot for a numeric column."""
    fig, ax = plt.subplots()
    sns.kdeplot(df[coluna].dropna(), ax=ax)
    ax.set_title(f"Densidade (KDE) de {coluna}")
    fig.tight_layout()
    return fig


def grafico_missing(df: pd.DataFrame) -> Figure:
    """Return a bar chart with the number (and percent) of missing values per column."""
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=missing.index, y=missing.values, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_ylabel('Missing Values')
    ax.set_title('Valores ausentes por coluna')
    fig.tight_layout()
    return fig


def grafico_correlacao(df: pd.DataFrame) -> Figure:
    """Return a correlation heatmap figure for numeric columns."""
    corr = df.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    # mask the upper triangle for readability
    mask = None
    try:
        import numpy as _np
        mask = _np.triu(_np.ones_like(corr, dtype=bool))
    except Exception:
        mask = None
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, mask=mask)
    ax.set_title('Matriz de Correlação')
    fig.tight_layout()
    return fig
