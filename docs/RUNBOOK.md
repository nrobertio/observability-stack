# Runbook: trigger each alert on purpose

The point of this stack is to see the alerts fire, not just to deploy it. Here is how to drive each one.

## HighErrorRate
Restart the app with injected errors, then send traffic:
```
docker compose stop app
ERROR_RATE=0.3 docker compose up -d app   # 30 percent of /work returns 500
k6 run loadtest/ramp.js
```
Within ~2-3 minutes the error ratio crosses 5 percent and HighErrorRate fires. Watch it in Alertmanager (9093) and the Grafana error panel. Reset with ERROR_RATE=0.0.

## HighLatencyP95
```
docker compose stop app
EXTRA_LATENCY_MS=700 docker compose up -d app
k6 run loadtest/ramp.js
```
p95 climbs above 500ms and HighLatencyP95 fires after 2m.

## TargetDown
```
docker compose stop app
```
Prometheus `up` for the app job goes to 0; TargetDown fires after 1m. Bring it back with `docker compose up -d app`.

## HighContainerCPU
Run the spike load while the app does real work:
```
k6 run loadtest/spike.js
```
cAdvisor reports container CPU; if it holds above 0.9 CPU for 2m the alert fires.

## Find a failing request in logs (Loki)
1. Trigger HighErrorRate as above.
2. In Grafana, Explore -> Loki, query: `{container=\"observability-stack-app-1\"} |= \"work failed\"`
3. You get the failing requests with their request_id, without touching the host.

## What to observe each time
- Does the alert fire at the threshold you expected, or is it noisy/late?
- Tune the `for:` duration and thresholds in prometheus/alerts.yml and re-run. That tuning loop is the real skill.