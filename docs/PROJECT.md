# Project Writeup: Observability and Performance Stack

Why this exists, how it was built, why each choice, benefits, and design trade-offs.

## 1. The problem it solves

You cannot operate what you cannot see. Most incidents are not "the server exploded"; they are slow degradation: error rate creeping up, p95 latency drifting, one container pinning CPU, logs scattered across hosts. This stack gives the three things an on-call engineer needs: metrics (what is happening), logs (why), and alerts (so you find out before customers do). It also includes load tests so you can prove the alerts actually fire under stress, rather than hoping they would.

## 2. How it was built

- A sample service instrumented with Prometheus client metrics (request counter by status, latency histogram) and structured JSON logs. It has tunable ERROR_RATE and EXTRA_LATENCY_MS so failures can be injected on demand.
- Prometheus scrapes the service plus cAdvisor (container metrics), and evaluates alert rules.
- Alertmanager routes alerts to a receiver (swap the webhook for Slack/email in real use).
- Grafana is provisioned as code: datasources and a dashboard come from files, so there is no clicking in the UI and the config is version-controlled.
- Loki plus Promtail collect logs from every container into one queryable place.
- k6 scenarios (ramp, spike, soak) drive load until the SLOs break.

## 3. Why each choice

- Metrics as histograms, not just averages: averages hide tail latency. The p95 from a histogram is what users actually feel, and what the SLO is written against.
- Alerts tied to SLOs (error rate, p95 latency, target down, CPU), not to raw numbers: alert on symptoms users notice, with a `for:` duration so a brief blip does not page anyone.
- Grafana provisioned from files: a dashboard clicked together in the UI is lost when the container is recreated. As code, it is reproducible and reviewable.
- Loki over a heavy ELK cluster: Loki indexes labels not full text, so it is cheap to run and pairs naturally with Prometheus labels. Right tool for log aggregation at this scale.
- cAdvisor for container CPU/memory: the infrastructure signal that explains a lot of application symptoms.
- Load tests committed alongside: an alert you have never seen fire is an alert you do not trust. k6 lets you trigger each one deliberately.

## 4. Benefits

- Find a failing request without SSHing into boxes: correlate a spike in the error panel with the matching Loki logs.
- Alerts fire on user-visible symptoms before the system is fully down.
- The whole observability config is code: reproducible across environments, reviewed in pull requests.
- You can prove reliability claims by running the load tests and watching the system hold or break.

## 5. Design notes and trade-offs

- RED vs USE: RED (Rate, Errors, Duration) for request-driven services, USE (Utilization, Saturation, Errors) for resources. This stack shows both: app RED metrics plus cAdvisor USE metrics.
- Why alert on p95 and error ratio, not CPU alone: CPU being high is not an incident if users are fine; error rate and latency are what the SLO protects. CPU is a supporting signal.
- `for:` duration and grouping: avoid alert spam from transient blips; group related alerts so one incident is one page.
- Logs vs metrics vs traces: metrics tell you something is wrong and alert cheaply; logs tell you what; traces (next step) tell you where across services.
- What I would add next: distributed tracing (Tempo/OpenTelemetry) to complete the three pillars, recording rules for expensive queries, and alert routing by severity to different receivers.

## 6. How to run it

```
docker compose up -d
# Grafana localhost:3000 (anon enabled), Prometheus 9090, Alertmanager 9093
k6 run loadtest/ramp.js
```
See RUNBOOK.md to trigger each alert on purpose.