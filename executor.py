"""Workflow executor client for testing purposes.

This script simulates task execution and communicates with a backend service
for status updates and final results.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Iterable

import httpx

CONFIG_PATH = Path(__file__).parent / "config.json"
STATUS_ENDPOINT = "/executor/status"
RESULT_ENDPOINT = "/executor/result"


def load_config(config_path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """Load executor configuration from JSON file."""
    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def post_json(client: httpx.Client, url: str, payload: Dict[str, Any]) -> None:
    """Send a JSON payload to the backend and log the outcome."""
    try:
        response = client.post(url, json=payload)
        response.raise_for_status()
        logging.debug("POST %s succeeded: %s", url, response.text)
    except httpx.HTTPError as exc:
        logging.error("POST %s failed: %s", url, exc)


def execute_task(task: Dict[str, Any], backend_url: str, client: httpx.Client) -> None:
    """Simulate task execution, sending periodic updates and final results."""
    task_id = task.get("id", "unknown")
    steps: Iterable[Dict[str, Any]] = task.get("steps", [])
    steps_list = list(steps)
    total_steps = len(steps_list)

    logging.info("Starting task %s with %d steps", task_id, total_steps)

    # Iterate over the cached list to avoid reloading from task.
    steps = steps_list or []
    start_time = time.time()

    for index, step in enumerate(steps, start=1):
        description = step.get("description", f"Step {index}")
        duration = float(step.get("duration", 1.0))

        logging.info("Executing step %d/%d: %s (%.1fs)", index, total_steps, description, duration)
        time.sleep(duration)

        progress_payload = {
            "task_id": task_id,
            "step": index,
            "total_steps": total_steps,
            "description": description,
            "progress": int((index / total_steps) * 100) if total_steps else 100,
            "timestamp": time.time(),
        }

        post_json(client, f"{backend_url}{STATUS_ENDPOINT}", progress_payload)

    end_time = time.time()
    result_payload = {
        "task_id": task_id,
        "status": task.get("result", {}).get("status", "success"),
        "output": task.get("result", {}).get("output", {}),
        "started_at": start_time,
        "finished_at": end_time,
        "duration": end_time - start_time,
    }

    post_json(client, f"{backend_url}{RESULT_ENDPOINT}", result_payload)
    logging.info("Task %s completed", task_id)


def build_demo_task() -> Dict[str, Any]:
    """Construct a simple task definition for demonstration purposes."""
    return {
        "id": "demo-task-001",
        "steps": [
            {"description": "Initialize environment", "duration": 1.0},
            {"description": "Process dataset", "duration": 2.0},
            {"description": "Finalize output", "duration": 1.5},
        ],
        "result": {
            "status": "success",
            "output": {
                "message": "Task completed successfully",
                "artifacts": ["log.txt", "results.json"],
            },
        },
    }


def setup_logging() -> None:
    """Configure logging for the executor."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def main() -> None:
    """Entry point for the executor script."""
    setup_logging()
    config = load_config()
    backend_url = config["backend_url"].rstrip("/")

    logging.info("Using backend URL: %s", backend_url)

    task = build_demo_task()

    with httpx.Client(timeout=httpx.Timeout(10.0, read=30.0)) as client:
        execute_task(task, backend_url, client)


if __name__ == "__main__":
    main()
