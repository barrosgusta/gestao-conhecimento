# function.py
from pathlib import Path
from typing import Union

import pandas as pd


def load_database(path: Union[str, Path] = "data/MundoEcommerce.parquet") -> pd.DataFrame:
    """Load the MundoEcommerce parquet dataset.

    Parameters
    ----------
    path : str | Path
        Path to the parquet file. Defaults to 'data/MundoEcommerce.parquet'.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.

    Raises
    ------
    RuntimeError
        If the file cannot be read.
    """
    p = Path(path)
    if not p.exists():
        raise RuntimeError(f"File not found: {p.resolve()}")
    try:
        df = pd.read_parquet(p)
        return df
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar a base ({p}): {e}")
