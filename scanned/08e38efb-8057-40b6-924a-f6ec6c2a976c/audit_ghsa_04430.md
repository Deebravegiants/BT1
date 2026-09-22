# [M] PyJWT: Unauthenticated DoS via unbounded Base64URL decoding of unused payload segment in b64=false detached JWS

## Summary
Severity: Medium
Advisory: GHSA-w7vc-732c-9m39
CVE: CVE-2026-48525
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-w7vc-732c-9m39
Type: github-advisory

## Affected
- PyPI: `pyjwt` — affected >=2.8.0 <2.13.0

## Details
> [!NOTE]
> Practical impact depends on whether request body-size limits are enforced upstream (proxy/web-server/framework). Deployments with typical body-size caps (≤2 MB) bound the amplifier significantly; deployments accepting larger token inputs are more exposed.

When verifying detached JWS tokens using the unencoded-payload option (`"b64": false`, RFC 7797), PyJWT performs **Base64URL decoding of the compact-serialization payload segment** *before* enforcing the detached-payload rules.

For `b64=false`, PyJWT later **discards** that decoded payload and replaces it with the caller-provided `detached_payload`. In practice, this turns the middle segment into an attacker-controlled “work amplifier”: a remote client can supply an arbitrarily large Base64URL payload segment that forces **CPU work + memory allocations** even if the signature is invalid.

This creates an **unauthenticated DoS** vector against any endpoint that verifies detached JWS using PyJWT.

---

## Affected Component(s)

* `jwt/api_jws.py`

  * `PyJWS.decode()` / `PyJWS.decode_complete()`
  * `_load()` (parsing and Base64URL decoding)

---

## Root Cause (exact logic flaw)

### What happens in the code

In `jwt/api_jws.py`, `decode_complete()` does the following (order matters):

* Calls `_load(jwt)` first, which decodes the token segments
* Only after that, checks `header.get("b64")` and if `False`, it replaces `payload = detached_payload` and rebuilds the signing input

This behavior is visible in `decode_complete()`:

* `_load(jwt)` happens **before** the `b64=false` handling
* then `payload = detached_payload` and `signing_input = ... detached_payload` happens afterward ([GitHub][1])

Inside `_load()`, PyJWT unconditionally performs:

* `payload = base64url_decode(payload_segment)`
  This is the expensive step the attacker can amplify ([GitHub][1])

### Why this becomes a vulnerability

For `b64=false` detached JWS, the payload segment in compact form is effectively **not needed** for verification in PyJWT’s own logic (since the library uses `detached_payload` as the real payload). Yet PyJWT still decodes it first, meaning:

* cost is paid **even when signature is invalid**
* the decoded bytes are **discarded**
* attacker controls the size of this cost via token length

---

## Impact (evidence-driven)

### Security impact

* **Unauthenticated remote DoS**: decoding work happens before signature rejection → attacker does not need signing key.
* **CPU amplification**: Base64URL decode time scales linearly with payload segment size.
* **Memory amplification**: decoded output allocates large byte buffers (tens of MB per request).
* **Operational impact**: request queueing / worker starvation under modest concurrency bursts.

### Standards context (RFC 7797)

RFC 7797 explicitly notes this option is used when payload is large and/or detached, and discusses interoperability requirements around marking it critical (“crit” with “b64”). ([IETF Datatracker][2])
(PyJWT supports `crit` validation, but the issue here is decode order / unbounded decode of an unused segment.)

---

## Affected Versions

* **Confirmed affected:** PyJWT **2.12.1** (tested from your local editable install and repo).
* **Likely affected:** all versions that include detached payload support for JWS decoding, which was introduced in **2.4.0** (“Add detached payload support for JWS encoding and decoding”). ([pyjwt.readthedocs.io][3])

(For GHSA, this phrasing is strong: “confirmed” + “likely since feature introduction”.)

---

# Threat Model 

### Typical real deployment

A service verifies signed HTTP requests or webhooks using detached JWS:

* token is provided in JSON body / query / header
* actual payload is the HTTP request body passed as `detached_payload`

### Attacker

* remote unauthenticated client
* can send requests to verify endpoint
* does **not** need a valid signature (invalid signature still triggers the expensive decode path)

### Attack chain

1. Attacker crafts a JWS compact token with header containing `"b64": false` and `crit:["b64"]`.
2. Attacker inflates the **payload segment** (middle segment) to millions of Base64URL characters.
3. Server calls `PyJWS.decode(...detached_payload=...)`.
4. PyJWT decodes the inflated segment (CPU + memory).
5. Signature is rejected afterward (401) — but resources already consumed.
6. Repeated requests or bursts cause queueing/worker starvation → DoS.

---

# Proof of Concept - file names + results

## PoC placement 

* [server_localhost.py](https://github.com/user-attachments/files/26132755/server_localhost.py)

* [client_localhost.py](https://github.com/user-attachments/files/26132757/client_localhost.py)

* [flood_localhost.py](https://github.com/user-attachments/files/26132760/flood_localhost.py)


---

## PoC # 1 - Localhost verification server

**File:** [server_localhost.py](https://github.com/user-attachments/files/26132755/server_localhost.py)

**Purpose:** real HTTP endpoint (`POST /verify`) that calls PyJWT detached verification and prints:
`ok / time_ms / peak_bytes / token_len / error`.

### Results (server console output)

```text
[+] Listening on http://127.0.0.1:8000
[+] POST /verify  JSON: {"token": "..."}

[127.0.0.1] ok=True  time_ms=0.102 peak_bytes=2624     token_len=117      err=None
[127.0.0.1] ok=False time_ms=2.012 peak_bytes=2000983  token_len=500078   err=InvalidSignatureError
[127.0.0.1] ok=True  time_ms=1.591 peak_bytes=2001061  token_len=500117   err=None

[127.0.0.1] ok=True  time_ms=0.065 peak_bytes=2304     token_len=117      err=None
[127.0.0.1] ok=False time_ms=7.534 peak_bytes=8000983  token_len=2000078  err=InvalidSignatureError
[127.0.0.1] ok=True  time_ms=6.347 peak_bytes=8001061  token_len=2000117  err=None

[127.0.0.1] ok=True  time_ms=0.066 peak_bytes=2304     token_len=117      err=None
[127.0.0.1] ok=False time_ms=23.034 peak_bytes=32000983 token_len=8000078 err=InvalidSignatureError
[127.0.0.1] ok=True  time_ms=22.097 peak_bytes=32001061 token_len=8000117 err=None
```

**Key takeaways from these results**

* At **8,000,000 chars**, a single invalid-signature request still causes:

  * **~23 ms** server work
  * **~32 MB** peak allocations
  * returns **401** (invalid signature) → attacker does not need key.

---

## PoC # 2 - Localhost network client

**File:** [client_localhost.py](https://github.com/user-attachments/files/26132757/client_localhost.py)
**Purpose:** generates baseline + (invalid signature) + (valid signature) tokens and sends them over HTTP to localhost server.

### Results (client output)

#### payload-chars = 500,000

```text
=== BASELINE (valid b64=false token) ===
HTTP: 200
client_wall_ms: 6.3499...
server_time_ms: 0.10197...
server_peak_bytes: 2624

=== ATTACK (INVALID signature - attacker needs no key) ===
HTTP: 401
client_wall_ms: 4.1010...
server_time_ms: 2.01217...
server_peak_bytes: 2000983
error: InvalidSignatureError

=== ATTACK (VALID signature - accepted path still wastes) ===
HTTP: 200
client_wall_ms: 3.6586...
server_time_ms: 1.59092...
server_peak_bytes: 2001061
```

#### payload-chars = 2,000,000

```text
=== BASELINE ===
HTTP: 200
server_time_ms: 0.06527...
server_peak_bytes: 2304

=== ATTACK (INVALID signature) ===
HTTP: 401
server_time_ms: 7.53430...
server_peak_bytes: 8000983

=== ATTACK (VALID signature) ===
HTTP: 200
server_time_ms: 6.34682...
server_peak_bytes: 8001061
```

#### payload-chars = 8,000,000

```text
=== BASELINE ===
HTTP: 200
server_time_ms: 0.06573...
server_peak_bytes: 2304

=== ATTACK (INVALID signature) ===
HTTP: 401
server_time_ms: 23.03403...
server_peak_bytes: 32000983

=== ATTACK (VALID signature) ===
HTTP: 200
server_time_ms: 22.09702...
server_peak_bytes: 32001061
```

**Why this is strong evidence**

* The server clearly does heavy work **before** rejecting invalid signatures.
* The “valid signature” case shows even accepted requests waste resources due to unused payload segment.

---

## PoC # 3 - Localhost flood / burst concurrency

**File:** [flood_localhost.py](https://github.com/user-attachments/files/26132760/flood_localhost.py)
**Purpose:** sends **N concurrent** invalid-signature requests over HTTP to demonstrate queueing/worker starvation.

### Results (your run: 20 concurrent @ 8,000,000 chars)

```text
total_wall_ms: 1374.5405770000616

(16, 401, 1156.4504789998864, 21.350951999920653, 32000983, 'InvalidSignatureError')
(19, 401, 1151.2852699997893, 21.208721999755653, 32000983, 'InvalidSignatureError')
(18, 401, 1102.7211239997996, 21.685218999664357, 32000983, 'InvalidSignatureError')
(13, 401, 1102.0718189997751, 21.26572200040755, 32000983, 'InvalidSignatureError')
(11, 401, 1095.9345460000804, 20.586017000368884, 32000983, 'InvalidSignatureError')
(17, 401, 1085.2552810001725, 22.893039000337012, 32000983, 'InvalidSignatureError')
(10, 401, 1078.3629560000918, 22.737160999895423, 32000983, 'InvalidSignatureError')
(7,  401, 1048.2011740000416, 22.476282000297942, 32000983, 'InvalidSignatureError')
(8,  401, 378.93017700025666, 21.377330999712285, 32000983, 'InvalidSignatureError')
(1,  401, 281.45106800002395, 21.34223099983501, 32000983, 'InvalidSignatureError')
```

**Interpretation**

* Each request still costs ~**20–23 ms** server processing and **~32 MB** peak allocations.
* But client-observed latency rises up to **~1.15 seconds** because requests queue behind each other → clear worker starvation/HoL blocking.
* All were rejected with **401 InvalidSignatureError** → still unauthenticated.

---

# Fix 

### Goal

Prevent unbounded resource consumption from an attacker-controlled payload segment that is unused in `b64=false` detached flow.

### Minimal change strategy

In `_load()` (or by refactoring parse order), **do not Base64-decode `payload_segment` until after you know whether `b64=false` applies**.

Two safe options:

1. **Reject non-empty payload segment when `b64=false`**

   * Parse header first
   * If `b64` is false and `payload_segment` is non-empty → raise `DecodeError` *before* decoding
   * Then verification uses `detached_payload` only

2. **Skip decoding payload segment entirely when `b64=false`**

   * Keep payload segment as raw bytes or empty
   * Use detached payload for signing input

This aligns with the idea that detached payload is the trusted payload input for verification; the compact payload segment should not become a resource amplification vector.

(Implementation context: the current decode order and unconditional `base64url_decode(payload_segment)` are visible in the file and line region around `_load()` and `decode_complete()` ([GitHub][1]).)

---

# Workarounds

* Enforce strict **max token length** at the HTTP boundary (proxy/gateway).
* Apply rate limiting on verification endpoints.
* If detached JWS (`b64=false`) is not needed in your app, reject tokens where header includes `"b64": false`.

## References
- https://github.com/jpadilla/pyjwt/security/advisories/GHSA-w7vc-732c-9m39
- https://nvd.nist.gov/vuln/detail/CVE-2026-48525
- https://github.com/jpadilla/pyjwt
- https://github.com/pypa/advisory-database/tree/main/vulns/pyjwt/PYSEC-2026-178.yaml
