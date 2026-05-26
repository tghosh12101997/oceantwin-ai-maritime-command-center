from __future__ import annotations

from dataclasses import dataclass
from math import radians, sin, cos, asin, sqrt
import pandas as pd


@dataclass
class RouteAssessment:
    origin: str
    destination: str
    distance_nm: float
    eta_days: float
    eta_risk_score: float
    eta_risk_label: str
    carbon_tco2: float
    eu_regulation_exposure: bool
    explanation: list[str]


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in nautical miles."""
    earth_radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = earth_radius_km * c
    return km * 0.539957


def risk_label(score: float) -> str:
    if score >= 0.70:
        return "High"
    if score >= 0.45:
        return "Medium"
    return "Low"


def estimate_carbon_tco2(distance_nm: float, vessel_teu: int, utilization: float = 0.75) -> float:
    """
    Simplified voyage-level estimate for a portfolio demo.
    Assumption: 10.5 gCO2 per TEU-km for a large container vessel.
    This is intentionally transparent and not a regulatory-grade calculation.
    """
    distance_km = distance_nm * 1.852
    active_teu = max(vessel_teu * utilization, 1)
    grams = distance_km * active_teu * 10.5
    return round(grams / 1_000_000, 2)


def assess_route(ports_df: pd.DataFrame, origin: str, destination: str, vessel_teu: int = 15000, speed_knots: float = 16.0) -> RouteAssessment:
    origin_row = ports_df.loc[ports_df["port_name"] == origin].iloc[0]
    destination_row = ports_df.loc[ports_df["port_name"] == destination].iloc[0]

    distance_nm = haversine_nm(origin_row.lat, origin_row.lon, destination_row.lat, destination_row.lon)
    eta_days = distance_nm / max(speed_knots, 1) / 24

    congestion_component = float((origin_row.congestion_score + destination_row.congestion_score) / 2)
    distance_component = min(distance_nm / 6500, 1.0)
    eu_exposure = bool(origin_row.eu_port or destination_row.eu_port)
    regulation_component = 0.12 if eu_exposure else 0.0

    score = round(min(0.55 * congestion_component + 0.33 * distance_component + regulation_component, 1.0), 2)
    label = risk_label(score)
    carbon = estimate_carbon_tco2(distance_nm, vessel_teu)

    explanation = [
        f"Origin congestion score: {origin_row.congestion_score:.2f}",
        f"Destination congestion score: {destination_row.congestion_score:.2f}",
        f"Approximate great-circle distance: {distance_nm:,.0f} nautical miles",
        f"EU maritime regulation exposure: {'yes' if eu_exposure else 'no'}",
    ]
    if score >= 0.70:
        explanation.append("Risk is elevated because distance, congestion, and regulation exposure combine into a high operational load.")
    elif score >= 0.45:
        explanation.append("Risk is moderate and should be monitored for delay propagation and customer notification impact.")
    else:
        explanation.append("Risk is low under the current simplified model.")

    return RouteAssessment(
        origin=origin,
        destination=destination,
        distance_nm=round(distance_nm, 1),
        eta_days=round(eta_days, 1),
        eta_risk_score=score,
        eta_risk_label=label,
        carbon_tco2=carbon,
        eu_regulation_exposure=eu_exposure,
        explanation=explanation,
    )
