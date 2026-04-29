import pandas as pd

def load_data(file):
    df = pd.read_csv(file)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["usage"] = pd.to_numeric(df["usage"], errors="coerce")

    df = df.dropna(subset=["date", "cost", "usage"])

    return df