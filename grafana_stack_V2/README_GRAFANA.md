# OceanTwin AI Grafana Dashboard

This stack starts PostgreSQL with seeded maritime demo data and Grafana with a provisioned dashboard.

## Run

```bash
docker compose down -v
docker compose up -d --force-recreate
```

Open Grafana:

```text
http://localhost:3000
```

Login:

```text
Username: admin
Password: oceantwin
```

Open:

```text
Dashboards → Browse → OceanTwin AI → OceanTwin AI - Maritime Command Center
```

## What is included

- FleetPulse world map with vessel positions
- Tracked vessels KPI
- Hapag-Lloyd watchlist KPI
- Average speed KPI
- High-risk vessel KPI
- Delay, cost, CO2, and stopped vessel KPIs
- Operational delay time series
- Delay by event type
- Severity mix
- CO2 impact by vessel
- Cost impact by port
- Port risk index
- Route risk table
- Fleet position table
- High-risk events feed

## Important

Grafana provisioning only reloads cleanly when old Docker volumes are removed. That is why the reset command uses `docker compose down -v`.
