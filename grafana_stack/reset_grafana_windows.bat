@echo off
echo Resetting OceanTwin Grafana stack...
docker compose down -v --remove-orphans
docker compose up -d --force-recreate
echo.
echo Open Grafana: http://localhost:3000
echo Username: admin
echo Password: oceantwin
pause
