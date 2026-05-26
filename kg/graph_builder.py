from __future__ import annotations

from pathlib import Path
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD
from services.risk_engine import RouteAssessment

OT = Namespace("https://oceantwin.ai/kg/")


def slug(value: str) -> str:
    return value.strip().replace(" ", "_").replace("/", "_")


def build_route_graph(assessment: RouteAssessment, vessel_name: str, company: str) -> Graph:
    g = Graph()
    g.bind("ot", OT)
    g.bind("rdfs", RDFS)

    vessel = OT[f"vessel/{slug(vessel_name)}"]
    company_uri = OT[f"company/{slug(company)}"]
    route = OT[f"route/{slug(assessment.origin)}_to_{slug(assessment.destination)}"]
    origin = OT[f"port/{slug(assessment.origin)}"]
    destination = OT[f"port/{slug(assessment.destination)}"]
    carbon = OT[f"carbon/{slug(assessment.origin)}_to_{slug(assessment.destination)}"]
    eta_risk = OT[f"risk/{slug(assessment.origin)}_to_{slug(assessment.destination)}"]

    g.add((vessel, RDF.type, OT.Vessel))
    g.add((vessel, RDFS.label, Literal(vessel_name)))
    g.add((company_uri, RDF.type, OT.ShippingCompany))
    g.add((company_uri, RDFS.label, Literal(company)))
    g.add((vessel, OT.operatedBy, company_uri))

    g.add((route, RDF.type, OT.MaritimeRoute))
    g.add((route, OT.originPort, origin))
    g.add((route, OT.destinationPort, destination))
    g.add((route, OT.distanceNm, Literal(assessment.distance_nm, datatype=XSD.float)))
    g.add((vessel, OT.assignedToRoute, route))

    g.add((origin, RDF.type, OT.Port))
    g.add((origin, RDFS.label, Literal(assessment.origin)))
    g.add((destination, RDF.type, OT.Port))
    g.add((destination, RDFS.label, Literal(assessment.destination)))

    g.add((eta_risk, RDF.type, OT.ETARisk))
    g.add((eta_risk, OT.riskScore, Literal(assessment.eta_risk_score, datatype=XSD.float)))
    g.add((eta_risk, OT.riskLabel, Literal(assessment.eta_risk_label)))
    g.add((route, OT.hasRisk, eta_risk))

    g.add((carbon, RDF.type, OT.CarbonEstimate))
    g.add((carbon, OT.estimatedTCO2, Literal(assessment.carbon_tco2, datatype=XSD.float)))
    g.add((route, OT.hasCarbonEstimate, carbon))

    if assessment.eu_regulation_exposure:
        reg = OT["regulation/EU_Maritime_Exposure"]
        g.add((reg, RDF.type, OT.RegulationExposure))
        g.add((reg, RDFS.label, Literal("EU maritime regulation exposure")))
        g.add((route, OT.subjectToRegulation, reg))

    return g


def export_graph(g: Graph, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(out), format="turtle")
    return out
