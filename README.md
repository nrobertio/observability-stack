# Observability and Performance Stack

A production-shaped observability stack: metrics (Prometheus), dashboards (Grafana), alerting (Alertmanager), centralized logs (Loki), and a load-testing harness (k6) against a sample service. The point is not to stand it up once, but to generate real alerts and real load and watch the system respond.

Maintained by nrobertio. A reference for SRE and platform work: metrics, logs, alerting and load testing wired together the way they are in production.

## What this demonstrates

- Metrics: Prometheus scrapes a sample service and node/container exporters.
- Dashboards: Grafana provisioned as code (datasources and dashboards from files, not clicked in the UI).
- Alerting: Alertmanager with real rules for high error rate, high latency, high CPU, and a target being down, routed to a receiver.
- Logs: Loki plus Promtail, so logs from every service are queryable in one place (find a failing request without SSHing into boxes).
- Load testing: k6 scripts that ramp traffic until latency and error rate degrade, so you can watch the alerts fire.

## Layout

```
app/                 sample instrumented service (Prometheus metrics, structured logs)
prometheus/          scrape config + alert rules
alertmanager/        routing + receiver config
grafana/             provisioned datasources and dashboards (as code)
loki/                Loki + Promtail config
loadtest/            k6 scenarios (ramp, spike, soak)
docker-compose.yml   brings the whole stack up locally
docs/                PROJECT.md, RUNBOOK.md
```

## Run it

```
docker compose up -d
# Grafana http://localhost:3000, Prometheus http://localhost:9090, Alertmanager http://localhost:9093
k6 run loadtest/ramp.js        # then watch the alerts fire in Alertmanager/Grafana
```

See docs/RUNBOOK.md for how to deliberately trigger each alert.

## License

MIT. See LICENSE.
