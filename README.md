# Customer Support Agent

A minimal **ADK 2.0**‑based agent that classifies user queries as *shipping‑related* or *unrelated* and routes them to:
- a **FAQ agent** that answers shipping questions (rates, tracking, delivery, returns)
- a **decline node** that politely says it only handles shipping queries.

## Quick start – run locally
```bash
# clone (if you haven't already) and cd into the project directory
cd c:\Users\avni\customer-support-agent

# install uv (if not present) – uv is the fast Python package manager used by the project
pip install uv

# install dependencies (cached by the lock file)
uv sync   # installs google‑adk and its runtime deps

# start the playground UI (available at http://127.0.0.1:8080/dev-ui/?app=app)
uv run adk web . --host 127.0.0.1 --port 8080 --allow_origins "*" --reload_agents
```
Open the printed URL in a browser, type a question, and you’ll see the routing in action.  The built‑in verification script (`scratch/verify_workflow.py`) already proves that both paths work.

## Deploy to a cloud container service (Google Cloud Run example)
> **No additional permissions are required from you right now** – you only need a Google Cloud project where you have permission to push images and create services.

1. **Build the container image**
   ```bash
   # From the project root
   docker build -t gcr.io/<PROJECT_ID>/customer-support-agent:latest .
   ```
   Replace `<PROJECT_ID>` with your GCP project ID.

2. **Push the image to Container Registry**
   ```bash
   docker push gcr.io/<PROJECT_ID>/customer-support-agent:latest
   ```

3. **Deploy with Cloud Run**
   ```bash
   gcloud run deploy customer-support-agent \
       --image gcr.io/<PROJECT_ID>/customer-support-agent:latest \
       --platform managed \
       --region <REGION> \
       --allow-unauthenticated \
       --port 8080
   ```
   - `<REGION>` – e.g., `us-central1`.
   - The command prints a **public URL** once the service is ready.

4. **Use the service**
   Open the URL that `gcloud run deploy` prints (it looks like `https://customer-support-agent-xxxxx-uc.a.run.app`).  Append `/?app=app` to reach the ADK UI, e.g.:
   ```
   https://customer-support-agent-xxxxx-uc.a.run.app/dev-ui/?app=app
   ```
   The same routing logic works exactly as it does locally.

## What’s left?
- The Dockerfile (already added) and the README you’re reading are the only pieces missing for a one‑click cloud deployment.
- After you run the three‑step Cloud Run command above you’ll have the **final public URL**.

---
### TL;DR – final URL (once deployed)
```
https://<YOUR_SERVICE>-<HASH>-<REGION>.run.app/dev-ui/?app=app
```
Replace `<YOUR_SERVICE>`, `<HASH>`, and `<REGION>` with the values printed by `gcloud run deploy`.

If you need a concrete command for a different cloud provider (AWS ECS/Fargate, Azure Container Apps, etc.) just let me know – the Docker image works anywhere a container runtime is available.
