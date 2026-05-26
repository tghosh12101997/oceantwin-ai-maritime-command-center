"""
Optional live AIS listener for AISStream.io.

Usage:
1. Copy .env.example to .env and add AISSTREAM_API_KEY.
2. Fill MMSI values in data/fleet_watchlist.csv.
3. Run: python services/ais_listener.py

The Streamlit app works with demo data even when this listener is not running.
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import websockets
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
WATCHLIST_PATH = ROOT / "data" / "fleet_watchlist.csv"
OUTPUT_PATH = ROOT / "data" / "live_positions.json"


def load_watchlist_mmsi() -> set[int]:
    df = pd.read_csv(WATCHLIST_PATH)
    values = set()
    for value in df.get("mmsi", pd.Series(dtype=str)).dropna().astype(str):
        value = value.strip()
        if value.isdigit():
            values.add(int(value))
    return values


def save_position(payload: dict) -> None:
    existing = []
    if OUTPUT_PATH.exists():
        try:
            existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []
    existing.append(payload)
    existing = existing[-500:]
    OUTPUT_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")


async def listen() -> None:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("AISSTREAM_API_KEY")
    if not api_key:
        raise RuntimeError("Missing AISSTREAM_API_KEY. Add it to .env first.")

    watchlist = load_watchlist_mmsi()
    if not watchlist:
        print("No MMSI values found in fleet_watchlist.csv. Listener will collect all position reports in the bounding box.")

    subscribe_message = {
        "APIKey": api_key,
        "BoundingBoxes": [[[-90, -180], [90, 180]]],
        "FilterMessageTypes": ["PositionReport"],
    }

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        await websocket.send(json.dumps(subscribe_message))
        print("Connected to AISStream. Listening for live AIS position reports...")
        async for message_json in websocket:
            message = json.loads(message_json)
            meta = message.get("MetaData", {})
            mmsi = meta.get("MMSI")
            if watchlist and mmsi not in watchlist:
                continue

            position = message.get("Message", {}).get("PositionReport", {})
            payload = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "vessel_name": meta.get("ShipName", "Unknown"),
                "mmsi": mmsi,
                "lat": position.get("Latitude"),
                "lon": position.get("Longitude"),
                "sog": position.get("Sog"),
                "heading": position.get("Cog"),
            }
            save_position(payload)
            print(payload)


if __name__ == "__main__":
    asyncio.run(listen())
