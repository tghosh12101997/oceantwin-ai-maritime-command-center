# Optional Grafana Stack

This folder gives you a real Grafana + PostgreSQL demo for OceanTwin AI.

## Run

```bash
docker compose up -d
```

Open Grafana:

- URL: http://localhost:3000
- User: admin
- Password: oceantwin

The PostgreSQL datasource and starter dashboard are provisioned automatically. You can create your own Grafana panels from the demo maritime tables.

## Demo tables

- `vessel_positions`
- `operational_events`

This is optional. The main portfolio dashboard runs with Streamlit and does not require Docker.
