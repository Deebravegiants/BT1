# [M] web3.py: SSRF via CCIP Read (EIP-3668) OffchainLookup URL handling

## Summary
Severity: Medium
Chain: Tooling
Component: web3
CVE: CVE-2026-40072
CWE: Server-Side Request Forgery (SSRF)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-5hr4-253g-cpx2
Type: github-advisory

## Details
## Summary

web3.py implements CCIP Read / `OffchainLookup` (EIP-3668) by performing HTTP requests to URLs supplied by smart contracts in `offchain_lookup_payload["urls"]`. The implementation uses these contract-supplied URLs directly (after `{sender}` / `{data}` template substitution) without any destination validation:

- No restriction to `https://` (and no opt-in gate for `http://`)
- No hostname or IP allowlist
- No blocking of private/reserved IP ranges (loopback, link-local, RFC1918)
- No redirect target validation (both `requests` and `aiohttp` follow redirects by default)

**CCIP Read is enabled by default** (`global_ccip_read_enabled = True` on all providers), meaning any application using web3.py's `.call()` method is exposed without explicit opt-in.

This results in **Server-Side Request Forgery (SSRF)** when web3.py is used in backend services, indexers, APIs, or any environment that performs `eth_call` / `.call()` against untrusted or user-supplied contract addresses. A malicious contract can force the web3.py process to issue HTTP requests to arbitrary destinations, including internal network services and cloud metadata endpoints.

---

## Why This Is a Vulnerability

The argument is not that CCIP Read itself is invalid or that web3.py should stop supporting EIP-3668. The issue is that, in server-side deployments (backends, indexers, bots, APIs), the current implementation doesn't provide destination policy controls, such as a validation/override hook, private-range blocking, or redirect target checks, which means contract controlled CCIP URLs can be used as an SSRF primitive.

This is consistent with EIP-3668's own security considerations, which recommends that client libraries "provide clients with a hook to override CCIP read calls, either by rewriting them to use a proxy service, or by denying them entirely" and that "this mechanism or another should be written so as to easily facilitate adding domains to allowlists or blocklists." The mitigations I'm suggesting are meant to align with that guidance without breaking CCIP Read support.

- **Default-on exposure.** CCIP Read is enabled by default on all web3.py providers (`global_ccip_read_enabled = True`). Users who never intend to use CCIP Read, and who may not even know the feature exists, are silently exposed. A feature that makes unsanitized outbound requests to attacker-controlled URLs should not be enabled by default without safety guardrails.

- **Library vs. application responsibility.** web3.py is a widely-used library. Expecting every downstream application to independently implement SSRF protections around `.call()` is unreasonable, especially for a feature that fires automatically and invisibly on a specific revert pattern. Safe defaults at the library level are the standard expectation for any library that issues outbound HTTP requests to externally-controlled URLs.

---

## Affected Code

### Sync CCIP handler

**File:** `web3/utils/exception_handling.py` (lines 42-58)

Contract-controlled URLs are requested via `requests` with no destination validation:

```python
session = requests.Session()
for url in offchain_lookup_payload["urls"]:
    formatted_url = URI(
        str(url)
        .replace("{sender}", str(formatted_sender))
        .replace("{data}", str(formatted_data))
    )

    try:
        if "{data}" in url and "{sender}" in url:
            response = session.get(formatted_url, timeout=DEFAULT_HTTP_TIMEOUT)
        else:
            response = session.post(
                formatted_url,
                json={"data": formatted_data, "sender": formatted_sender},
                timeout=DEFAULT_HTTP_TIMEOUT,
            )
```

(The request is issued before response validation; subsequent logic parses JSON and enforces a `"data"` field.)

Key observations:
- `requests` follows redirects by default (`allow_redirects=True`).
- No `allow_redirects=False` is set.
- No validation of `formatted_url` before the request.
- The placeholder check (`if "{data}" in url`) operates on the raw `url` value from the payload (before `str()` conversion), not on the already-formatted `formatted_url`. If `url` is not a plain `str` (e.g., a `URI` type), the `in` check may behave differently than intended.

### Async CCIP handler

**File:** `web3/utils/async_exception_handling.py` (lines 45-63)

Same pattern with `aiohttp`:

```python
session = ClientSession()
for url in offchain_lookup_payload["urls"]:
    formatted_url = URI(
        str(url)
        .replace("{sender}", str(formatted_sender))
        .replace("{data}", str(formatted_data))
    )

    try:
        if "{data}" in url and "{sender}" in url:
            response = await session.get(
                formatted_url, timeout=ClientTimeout(DEFAULT_HTTP_TIMEOUT)
            )
        else:
            response = await session.post(
                formatted_url,
                json={"data": formatted_data, "sender": formatted_sender},
                timeout=ClientTimeout(DEFAULT_HTTP_TIMEOUT),
            )
```

Key observations:
- `aiohttp` follows redirects by default.
- No redirect or destination validation.
- Same raw-`url` placeholder check issue as the sync handler.

### Default-on invocation path

**File:** `web3/providers/base.py` (line 66) and `web3/providers/async_base.py` (line 79):

```python
global_ccip_read_enabled: bool = True
```

**File:** `web3/eth/eth.py` (lines 222-266) and `web3/eth/async_eth.py` (lines 243-287):

The `.call()` method automatically invokes `handle_offchain_lookup()` / `async_handle_offchain_lookup()` when a contract reverts with `OffchainLookup`, up to `ccip_read_max_redirects` times (default: 4). No user interaction or explicit opt-in is required beyond the default configuration.

---

## Security Impact

### 1. Blind SSRF (Primary Impact)

A malicious contract can supply URLs that cause the web3.py process to issue HTTP GET or POST requests to:

- **Loopback services:** `http://127.0.0.1:<port>/...`, `http://localhost/...`
- **Cloud metadata endpoints:** `http://169.254.169.254/latest/meta-data/iam/security-credentials/`
- **Internal network services:** any RFC1918 address (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`)
- **Arbitrary external destinations**

The request is made from the web3.py process. This alone constitutes SSRF -- the attacker controls the destination of an outbound request from the victim's infrastructure.

**Note on response handling:** The CCIP handler expects a JSON response containing a `"data"` field. If the target endpoint does not return valid JSON with this key, the handler raises `Web3ValidationError` or continues to the next URL. This means:

- The raw response body is **not** directly returned to the attacker in most cases (blind SSRF).
- However, the request itself is the primary threat: it can reach internal services, trigger side effects on internal APIs, and serve as a network probe.
- On AWS with IMDSv1, a GET to `http://169.254.169.254/...` returns credentials in plaintext. While the CCIP handler would fail to parse this as JSON, the request itself reaches the metadata service. If an internal endpoint returns JSON containing a `"data"` field (or can be coerced to), the handler may accept it and use it in the on-chain callback, creating a potential exfiltration path.

### 2. Redirect-Based SSRF Amplification

Both `requests` and `aiohttp` follow HTTP redirects by default. The CCIP handlers use the final response without validating the final resolved URL.

- **Sync:** `web3/utils/exception_handling.py` -- `session.get()` with default `allow_redirects=True`
- **Async:** `web3/utils/async_exception_handling.py` -- `session.get()` with default redirect following

A contract-supplied URL can point to an attacker-controlled server that issues a `302` redirect to `http://169.254.169.254/...` or any internal endpoint. This defeats naive URL-prefix checks that an application might add, expanding the SSRF surface.

### 3. Internal Network Probing

By varying the URLs supplied in the `OffchainLookup` revert payload, an attacker can:

- Probe internal network topology (open ports, reachable hosts) based on response timing and error behavior
- Trigger side effects on internal APIs that accept GET or POST requests without authentication
- Map cloud infrastructure by querying metadata endpoints

### 4. POST-Based SSRF

When the contract-supplied URL does **not** contain both `{sender}` and `{data}` placeholders, the handler switches to `session.post()` with a JSON body. This means the attacker can cause the victim to issue **POST requests with a controlled JSON body** (`{"data": ..., "sender": ...}`) to arbitrary destinations, increasing the potential for triggering state-changing operations on internal services.

---

## Proof of Concept

### Prerequisites

- Python environment with `web3` installed
- No network access or blockchain connection required (the PoC calls the handler function directly)

### Step 1: Start a local HTTP listener

```bash
python -m http.server 9999
```

### Step 2: Run the reproduction script

```bash
python repro_ssrf.py
```

### Step 3: Observe

The HTTP server logs will show an inbound request to a path like `/SSRF_DETECTION_SUCCESS?sender=...&data=...`, confirming that `handle_offchain_lookup()` issued an outbound HTTP request to the contract-supplied URL without any destination validation.

The script will then print an error (the local HTTP server does not return the expected JSON), but the request has already been sent -- the SSRF occurs before any response validation.

### Reproduction script (`repro_ssrf.py`)

```python
from web3.types import TxParams
from web3.utils.exception_handling import handle_offchain_lookup


def reproduce_ssrf():
    target_address = "0x0000000000000000000000000000000000000001"

    payload = {
        "sender": target_address,
        "callData": "0x1234",
        "callbackFunction": "0x12345678",
        "extraData": "0x90ab",
        "urls": [
            "http://127.0.0.1:9999/SSRF_DETECTION_SUCCESS?sender={sender}&data={data}"
        ],
    }

    transaction: TxParams = {"to": target_address}

    print(f"Triggering CCIP Read handler with URL: {payload['urls'][0]}")

    try:
        handle_offchain_lookup(payload, transaction)
    except Exception as e:
        print(f"Expected failure after request was sent: {e}")


if __name__ == "__main__":
    reproduce_ssrf()
```

### Real-world attack scenario

In a production setting, the attacker would:

1. Deploy a malicious contract that reverts with `OffchainLookup`, supplying URLs pointing to internal services (e.g., `http://169.254.169.254/latest/meta-data/iam/security-credentials/`).
2. Cause a backend service (indexer, API, bot) to call that contract via `eth_call` / `.call()`.
3. web3.py automatically triggers CCIP Read, issuing the HTTP request from the backend's network context.

No special permissions or contract interactions beyond a standard `eth_call` are required.

---

## Suggested Remediation

### 1. Restrict URL schemes (safe default)

Allow only `https://` by default. Provide an explicit opt-in flag (e.g., `ccip_read_allow_http=True`) for `http://`.

### 2. Block private/reserved IP destinations by default

Before issuing the request, resolve the hostname and reject connections to:

- `127.0.0.0/8` (loopback)
- `169.254.0.0/16` (link-local / cloud metadata)
- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC1918)
- `::1`, `fe80::/10` (IPv6 loopback / link-local)
- `0.0.0.0/8`

### 3. Disable or validate redirects

Either:
- Set `allow_redirects=False` on the HTTP requests, or
- Validate each redirect target against the same destination policy before following it

### 4. Provide a URL validator hook

Allow users to supply a custom URL validation callback for CCIP Read URLs (e.g., a hostname allowlist, gateway pinning, or custom policy). This enables advanced users to configure CCIP Read for their specific trust model.

### 5. Consider stronger default safety signaling (or default-off in server-side contexts)

EIP-3668 encourages keeping CCIP Read enabled for calls, so this may not be desirable as a universal default change. However, for server-side deployments, consider either:
- a clearly documented “safe mode” preset (destination validation + redirect checks + private-range blocking), or
- stronger warnings / examples showing how to disable CCIP Read (`ccip_read_enabled=False` or `global_ccip_read_enabled=False`) when calling untrusted contracts.

At minimum, document the SSRF risk prominently in the CCIP Read docs.
