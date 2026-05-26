# OceanTwin AI Grafana Stack

Start from this folder only:

```bash
cd grafana_stack
docker compose down -v
docker compose up -d --force-recreate
```

Open Grafana:

```text
http://localhost:3000
```

Login:

```text
admin / oceantwin
```

Open the dashboard here:

Dashboards → OceanTwin AI → OceanTwin AI Command Center

If the dashboard list is empty, check provisioning logs:

```bash
docker logs oceantwin-grafana | grep -i provisioning
```

The PostgreSQL datasource is provisioned with UID `oceantwin-postgres` and the dashboard is provisioned with UID `oceantwin-command-center`.
