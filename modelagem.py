from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from function import load_database

WAREHOUSE_DIR = Path("data/warehouse")


def _prep_dates(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([], dtype='datetime64[ns]')
    return pd.to_datetime(df[col], errors='coerce')


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    order_dates = _prep_dates(df, "Order Date")
    ship_dates = _prep_dates(df, "Shipping Date")
    all_dates = pd.Series(pd.concat([order_dates, ship_dates]).dropna().unique()).sort_values()
    dim = pd.DataFrame({"Date": all_dates})
    dim["DateKey"] = dim["Date"].dt.strftime("%Y%m%d").astype(int)
    dim["Year"] = dim["Date"].dt.year
    dim["Quarter"] = dim["Date"].dt.quarter
    dim["Month"] = dim["Date"].dt.month
    dim["MonthName"] = dim["Date"].dt.month_name()  # sem locale para evitar erro de sistema
    dim["Day"] = dim["Date"].dt.day
    dim["DayOfWeek"] = dim["Date"].dt.weekday + 1
    dim["DayOfWeekName"] = dim["Date"].dt.day_name()
    dim["WeekOfYear"] = dim["Date"].dt.isocalendar().week.astype(int)
    return dim[
        ["DateKey", "Date", "Year", "Quarter", "Month", "MonthName", "Day", "DayOfWeek", "DayOfWeekName", "WeekOfYear"]]


def _surrogate_key(df: pd.DataFrame, name: str) -> pd.DataFrame:
    df = df.copy()
    df.insert(0, name, range(1, len(df) + 1))
    return df


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["Customer ID", "Customer Name", "Segment"] if c in df.columns]
    dim = df[cols].drop_duplicates().sort_values(cols).reset_index(drop=True)
    return _surrogate_key(dim, "CustomerKey")


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["Product Category", "Product"] if c in df.columns]
    dim = df[cols].drop_duplicates().sort_values(cols).reset_index(drop=True)
    return _surrogate_key(dim, "ProductKey")


def build_dim_geography(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["Country", "Region", "State", "City"] if c in df.columns]
    dim = df[cols].drop_duplicates().sort_values(cols).reset_index(drop=True)
    return _surrogate_key(dim, "GeoKey")


def build_dim_ship_mode(df: pd.DataFrame) -> pd.DataFrame:
    if "Ship Mode" not in df.columns:
        return pd.DataFrame(columns=["ShipModeKey", "Ship Mode"])
    dim = (df[["Ship Mode"]].drop_duplicates().sort_values("Ship Mode").reset_index(drop=True))
    return _surrogate_key(dim, "ShipModeKey")


def build_dim_order_priority(df: pd.DataFrame) -> pd.DataFrame:
    if "Order Priority" not in df.columns:
        return pd.DataFrame(columns=["OrderPriorityKey", "Order Priority"])
    dim = (df[["Order Priority"]].drop_duplicates().sort_values("Order Priority").reset_index(drop=True))
    return _surrogate_key(dim, "OrderPriorityKey")


def build_fact_sales(df: pd.DataFrame, dims: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    f = df.copy()
    # Map datas para keys
    if "Order Date" in f.columns:
        date_lookup = dict(zip(dims["dim_date"]["Date"], dims["dim_date"]["DateKey"]))
        f["OrderDateKey"] = pd.to_datetime(f["Order Date"], errors='coerce').map(date_lookup)
    else:
        f["OrderDateKey"] = None
    if "Shipping Date" in f.columns:
        date_lookup = dict(zip(dims["dim_date"]["Date"], dims["dim_date"]["DateKey"]))
        f["ShipDateKey"] = pd.to_datetime(f["Shipping Date"], errors='coerce').map(date_lookup)
    else:
        f["ShipDateKey"] = None

    def merge_key(frame: pd.DataFrame, dim: pd.DataFrame, on_cols, key_name):
        if not on_cols or not all(c in frame.columns for c in on_cols):
            frame[key_name] = None
            return frame
        tmp = dim.copy()
        frame = frame.merge(tmp[[key_name] + on_cols], how='left', on=on_cols)
        return frame

    f = merge_key(f, dims["dim_customer"], [c for c in ["Customer ID", "Customer Name", "Segment"] if c in f.columns],
                  "CustomerKey")
    f = merge_key(f, dims["dim_product"], [c for c in ["Product Category", "Product"] if c in f.columns], "ProductKey")
    f = merge_key(f, dims["dim_geography"], [c for c in ["Country", "Region", "State", "City"] if c in f.columns],
                  "GeoKey")
    f = merge_key(f, dims["dim_ship_mode"], ["Ship Mode"] if "Ship Mode" in f.columns else [], "ShipModeKey")
    f = merge_key(f, dims["dim_order_priority"], ["Order Priority"] if "Order Priority" in f.columns else [],
                  "OrderPriorityKey")

    measures = [c for c in ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost", "Aging"] if c in f.columns]

    fact_cols = [
                    "Order ID", "OrderDateKey", "ShipDateKey", "CustomerKey", "ProductKey", "GeoKey", "ShipModeKey",
                    "OrderPriorityKey",
                ] + measures
    fact = f[fact_cols].copy()
    fact.rename(columns={"Order ID": "OrderID", "Shipping Cost": "ShippingCost"}, inplace=True)
    return fact


def build_star_schema(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    dim_date = build_dim_date(df)
    dim_customer = build_dim_customer(df)
    dim_product = build_dim_product(df)
    dim_geo = build_dim_geography(df)
    dim_ship = build_dim_ship_mode(df)
    dim_priority = build_dim_order_priority(df)
    dims = {
        "dim_date": dim_date,
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_geography": dim_geo,
        "dim_ship_mode": dim_ship,
        "dim_order_priority": dim_priority,
    }
    fact_sales = build_fact_sales(df, dims)
    return {**dims, "fact_sales": fact_sales}


def save_star_schema(tables: Dict[str, pd.DataFrame], out_dir: Path = WAREHOUSE_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_parquet(out_dir / f"{name}.parquet", index=False)


def load_star_schema(out_dir: Path = WAREHOUSE_DIR, build_if_missing: bool = True) -> Dict[str, pd.DataFrame]:
    expected = [
        "dim_date.parquet", "dim_customer.parquet", "dim_product.parquet", "dim_geography.parquet",
        "dim_ship_mode.parquet", "dim_order_priority.parquet", "fact_sales.parquet"
    ]
    if not out_dir.exists() or any(not (out_dir / f).exists() for f in expected):
        if not build_if_missing:
            raise FileNotFoundError("Arquivos do modelo dimensional não encontrados.")
        base = load_database()
        star = build_star_schema(base)
        save_star_schema(star, out_dir)
    loaded: Dict[str, pd.DataFrame] = {}
    for f in expected:
        name = f.replace('.parquet', '')
        loaded[name] = pd.read_parquet(out_dir / f)
    return loaded


__all__ = [
    'build_star_schema', 'save_star_schema', 'load_star_schema'
]


def main():  # manual
    df = load_database()
    tables = build_star_schema(df)
    save_star_schema(tables)
    print(f"Tabelas geradas em {WAREHOUSE_DIR}/")
    for k, v in tables.items():
        print(k, v.shape)


if __name__ == "__main__":
    main()
