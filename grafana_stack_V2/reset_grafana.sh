#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
docker compose down -v
docker compose up -d --force-recreate
echo "Open http://localhost:3000 and go to Dashboards > OceanTwin AI"
