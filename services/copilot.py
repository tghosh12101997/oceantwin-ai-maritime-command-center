from __future__ import annotations

from services.risk_engine import RouteAssessment


def answer_question(question: str, assessment: RouteAssessment, vessel_name: str, company: str) -> str:
    """Rule-based copilot for the MVP. Replace this with an LLM/RAG layer later."""
    q = question.lower().strip()

    if not q:
        return "Ask me about ETA risk, carbon impact, EU exposure, or operational actions for this route."

    if "risk" in q or "delay" in q or "eta" in q:
        return (
            f"{vessel_name} on {assessment.origin} → {assessment.destination} has a "
            f"{assessment.eta_risk_label.lower()} ETA risk score of {assessment.eta_risk_score}. "
            f"The main drivers are port congestion, voyage distance of about {assessment.distance_nm:,.0f} nm, "
            f"and {'EU regulatory exposure' if assessment.eu_regulation_exposure else 'limited EU regulatory exposure'}."
        )

    if "carbon" in q or "co2" in q or "emission" in q:
        return (
            f"The simplified voyage carbon estimate is {assessment.carbon_tco2:,.0f} tCO₂. "
            "This is a transparent portfolio estimate, not a compliance-grade MRV calculation. "
            "The next improvement would be to include real vessel speed, engine profile, fuel type, load factor, and weather routing."
        )

    if "eu" in q or "regulation" in q or "fueleu" in q or "ets" in q:
        return (
            f"EU exposure is {'present' if assessment.eu_regulation_exposure else 'not detected'} for this selected route. "
            "The MVP marks exposure when origin or destination is an EU port. A production version should model port-call legs, voyage segments, fuel type, MRV data, and regulation-specific scope rules."
        )

    if "action" in q or "recommend" in q or "what should" in q:
        return (
            f"Recommended action: monitor {assessment.destination} congestion, alert high-priority customers if ETA risk rises, "
            "and compare a lower-speed carbon-saving scenario against delivery commitment risk."
        )

    return (
        f"For {company}'s watched vessel {vessel_name}, the selected route {assessment.origin} → {assessment.destination} "
        f"has {assessment.eta_risk_label.lower()} ETA risk, estimated transit time of {assessment.eta_days} days, "
        f"and a simplified carbon estimate of {assessment.carbon_tco2:,.0f} tCO₂."
    )
