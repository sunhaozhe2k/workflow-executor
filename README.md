# Workflow Executor Client

A lightweight Python client that simulates workflow execution and reports
progress/results to a backend API. This project is intended for testing and
integration experiments.

## Project Structure

```
.
├── config.json
├── executor.py
├── README.md
└── requirements.txt
```

## Configuration

Edit `config.json` to point to your backend service:

```
{
  "backend_url": "http://localhost:8000"
}
```

## Running the Executor

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Execute the client:

   ```bash
   python executor.py
   ```

The script will simulate a demo task, send status updates to
`/executor/status`, and report final results to `/executor/result` on the
configured backend.

## Notes

- The demo task uses `time.sleep()` calls to simulate work.
- HTTP requests are performed with [httpx](https://www.python-httpx.org/).
