#!/usr/bin/env python3

import argparse
import concurrent.futures
import os
import statistics
import threading
import time
from collections import defaultdict

import requests


TARGET_URL = "http://10.211.55.18:8086"
ORGANIZATION = "Iot"
SOURCE_BUCKET = "Security"
METRICS_BUCKET = "LoadTest"

# Sicherheitsgrenzen für das lokale Labor
MAX_RPS = 500
MAX_WORKERS = 100
MAX_DURATION = 900

results_lock = threading.Lock()
results = defaultdict(list)


def run_query(token: str) -> tuple[bool, float, int]:
    flux_query = f'''
from(bucket: "{SOURCE_BUCKET}")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "mqtt_sensor")
  |> limit(n: 1000)
'''

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/vnd.flux",
        "Accept": "application/csv",
    }

    start = time.perf_counter()

    try:
        response = requests.post(
            f"{TARGET_URL}/api/v2/query",
            params={"org": ORGANIZATION},
            headers=headers,
            data=flux_query,
            timeout=10,
        )

        latency_ms = (time.perf_counter() - start) * 1000
        success = response.status_code == 200

        return success, latency_ms, response.status_code

    except requests.RequestException:
        latency_ms = (time.perf_counter() - start) * 1000
        return False, latency_ms, 0


def write_metrics(
    token: str,
    timestamp: int,
    requests_count: int,
    successes: int,
    errors: int,
    average_ms: float,
    p95_ms: float,
) -> None:
    line_protocol = (
        f"loadtest,target=influxdb "
        f"requests={requests_count}i,"
        f"successes={successes}i,"
        f"errors={errors}i,"
        f"avg_latency_ms={average_ms:.2f},"
        f"p95_latency_ms={p95_ms:.2f} "
        f"{timestamp}"
    )

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "text/plain; charset=utf-8",
    }

    try:
        response = requests.post(
            f"{TARGET_URL}/api/v2/write",
            params={
                "org": ORGANIZATION,
                "bucket": METRICS_BUCKET,
                "precision": "s",
            },
            headers=headers,
            data=line_protocol,
            timeout=5,
        )

        if response.status_code not in (204, 200):
            print(
                f"Warnung: Metriken konnten nicht geschrieben werden: "
                f"HTTP {response.status_code}"
            )

    except requests.RequestException as error:
        print(f"Warnung beim Schreiben der Metriken: {error}")


def calculate_p95(values: list[float]) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = max(0, int(len(sorted_values) * 0.95) - 1)
    return sorted_values[index]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kontrollierter InfluxDB-Lasttest"
    )

    parser.add_argument("--rps", type=int, default=10)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--workers", type=int, default=10)

    args = parser.parse_args()

    if args.rps < 1 or args.rps > MAX_RPS:
        raise SystemExit(f"--rps muss zwischen 1 und {MAX_RPS} liegen.")

    if args.workers < 1 or args.workers > MAX_WORKERS:
        raise SystemExit(
            f"--workers muss zwischen 1 und {MAX_WORKERS} liegen."
        )

    if args.duration < 1 or args.duration > MAX_DURATION:
        raise SystemExit(
            f"--duration muss zwischen 1 und {MAX_DURATION} Sekunden liegen."
        )

    token = os.environ.get("INFLUX_TOKEN")

    if not token:
        raise SystemExit(
            "Fehler: Umgebungsvariable INFLUX_TOKEN ist nicht gesetzt."
        )

    print("Lasttest wird gestartet")
    print(f"Ziel:       {TARGET_URL}")
    print(f"Rate:       {args.rps} Anfragen/Sekunde")
    print(f"Dauer:      {args.duration} Sekunden")
    print(f"Worker:     {args.workers}")
    print()

    started_at = time.monotonic()
    next_request = started_at
    futures = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.workers
    ) as executor:

        while time.monotonic() - started_at < args.duration:
            now = time.monotonic()

            if now < next_request:
                time.sleep(next_request - now)

            futures.append(executor.submit(run_query, token))
            next_request += 1 / args.rps

        completed = 0

        for future in concurrent.futures.as_completed(futures):
            success, latency_ms, status_code = future.result()
            completed += 1

            second = int(time.time())

            with results_lock:
                results[second].append(
                    {
                        "success": success,
                        "latency_ms": latency_ms,
                        "status_code": status_code,
                    }
                )

            if completed % 100 == 0:
                print(f"{completed}/{len(futures)} Anfragen abgeschlossen")

    total_requests = 0
    total_successes = 0
    all_latencies = []

    for second, entries in sorted(results.items()):
        latencies = [entry["latency_ms"] for entry in entries]
        successes = sum(1 for entry in entries if entry["success"])
        errors = len(entries) - successes

        average_ms = statistics.mean(latencies) if latencies else 0.0
        p95_ms = calculate_p95(latencies)

        write_metrics(
            token=token,
            timestamp=second,
            requests_count=len(entries),
            successes=successes,
            errors=errors,
            average_ms=average_ms,
            p95_ms=p95_ms,
        )

        total_requests += len(entries)
        total_successes += successes
        all_latencies.extend(latencies)

    total_errors = total_requests - total_successes
    total_average = (
        statistics.mean(all_latencies) if all_latencies else 0.0
    )
    total_p95 = calculate_p95(all_latencies)

    print()
    print("Lasttest beendet")
    print(f"Anfragen:          {total_requests}")
    print(f"Erfolgreich:       {total_successes}")
    print(f"Fehler:            {total_errors}")
    print(f"Ø Antwortzeit:     {total_average:.2f} ms")
    print(f"95%-Antwortzeit:   {total_p95:.2f} ms")


if __name__ == "__main__":
    main()
