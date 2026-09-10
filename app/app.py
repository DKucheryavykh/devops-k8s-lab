from flask import Flask, jsonify, Response
import os
import socket
import time

app = Flask(__name__)

START_TIME = time.time()
REQUEST_COUNT = 0


@app.get("/")
def index():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    return jsonify(
        service="devops-k8s-lab",
        hostname=socket.gethostname(),
        environment=os.getenv("APP_ENV", "development"),
        message=os.getenv(
            "APP_MESSAGE",
            "Hello from DevOps Kubernetes Lab!"
        )
    )


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/ready")
def ready():
    return jsonify(status="ready"), 200


@app.get("/metrics")
def metrics():
    uptime = int(time.time() - START_TIME)

    body = f"""# HELP app_requests_total Total requests to /
# TYPE app_requests_total counter
app_requests_total {REQUEST_COUNT}
# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}
"""

    return Response(body, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
