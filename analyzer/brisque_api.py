import json
import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

METRICS_JSON = "/app/metrics/brisque_metrics.json"

app = FastAPI(title="BRISQUE Metrics API")


@app.get("/metrics")
def get_metrics():
    if not os.path.exists(METRICS_JSON):
        # Decoder not yet started or first second not elapsed
        raise HTTPException(status_code=503, detail="Metrics not yet available")

    try:
        with open(METRICS_JSON, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise HTTPException(status_code=503, detail=f"Could not read metrics: {e}")

    # Report stale metrics if decoder stopped writing
    age = int(time.time()) - data.get("timestamp_sec", 0)
    if age > 5:
        data["stale"] = True
        data["stale_seconds"] = age

    return JSONResponse(content=data)


@app.get("/health")
def health():
    return {"status": "ok"}