from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_ports() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "ports.csv")
    df["eu_port"] = df["eu_port"].astype(str).str.lower().eq("true")
    return df


def load_fleet() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "fleet_watchlist.csv")


def load_demo_vessels() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "demo_vessels.csv")


def load_live_positions() -> pd.DataFrame:
    path = ROOT / "data" / "live_positions.json"
    if not path.exists():
        return pd.DataFrame()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()
