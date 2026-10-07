# Sample service instrumented for Prometheus and structured logging.
# Exposes /metrics, a /work endpoint with tunable latency and error rate so we
# can drive the alerts, plus health endpoints.
import logging
import os
import random
import time

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","msg":"%(message)s"}')
log = logging.getLogger("app")

app = FastAPI(title="obs-sample")

REQS = Counter("app_requests_total", "Total requests", ["endpoint", "status"])
LAT = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])

# Tunable failure injection via env, so load tests can push the system.
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.0"))
EXTRA_LATENCY_MS = int(os.getenv("EXTRA_LATENCY_MS", "0"))


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/work")
def work():
    start = time.time()
    endpoint = "/work"
    time.sleep(EXTRA_LATENCY_MS / 1000.0 + random.uniform(0, 0.05))
    if random.random() < ERROR_RATE:
        REQS.labels(endpoint, "500").inc()
        LAT.labels(endpoint).observe(time.time() - start)
        log.error("work failed request_id=%s", random.randint(1000, 9999))
        return Response("error", status_code=500)
    REQS.labels(endpoint, "200").inc()
    LAT.labels(endpoint).observe(time.time() - start)
    log.info("work ok request_id=%s", random.randint(1000, 9999))
    return {"result": "ok"}
