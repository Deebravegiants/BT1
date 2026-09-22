# [M] Open WebUI: Unauthenticated endpoint can trigger embedding generation (cost/DoS)

## Summary
Severity: Medium
Advisory: GHSA-m69w-p7m4-585j
CVE: CVE-2026-45667
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-m69w-p7m4-585j
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.0

## Details
### Summary
GET `/api/v1/memories/ef` is accessible without authentication and executes `request.app.state.EMBEDDING_FUNCTION(...)`. This allows any unauthenticated caller to trigger embedding generation which can lead to direct cost exposure if a paid provider is used.
Code reference: `backend/open_webui/routers/memories.py` (@router.get("/ef") -> calls `request.app.state.EMBEDDING_FUNCTION("hello world"))`.


### Details
GET `/api/v1/memories/ef` is reachable without authentication and triggers request.app.state.EMBEDDING_FUNCTION("hello world"). This crosses an intended security boundary by allowing unauthenticated users to invoke potentially expensive embedding computation and/or paid upstream embedding APIs.

### PoC
1. Start Open WebUI in default configuration (no special env hardening; default ENABLE_MEMORIES is true).
2. From an unauthenticated client (no cookies/Authorization header), call:
      curl -i http://\<host\>:\<port\>/api/v1/memories/ef
   3. Observe the server performs embedding generation and returns a response like:
   - HTTP 200 with JSON containing the result.

How it can be abused / attacker actions:

- Send repeated requests to `/api/v1/memories/ef` to:
  - consume CPU/GPU resources (DoS)
  - generate sustained outbound usage to embedding providers if configured (cost + rate-limit exhaustion)
  - degrade latency/availability for legitimate users
 
### Impact
If embeddings are configured to use paid/remote providers (OpenAI/Azure/etc), an attacker can generate unlimited requests and incur charges.

## Resolution

Fixed in commit [e5035ea31](https://github.com/open-webui/open-webui/commit/e5035ea31e179977e805a7032c979ff59a71860a), first released in **v0.8.0** (Feb 2026). The `/api/v1/memories/ef` route was removed entirely. It was a diagnostic/debug-style endpoint that hard-coded `"hello world"` through the embedding function without any authentication dependency; there was no legitimate caller that depended on it, so deletion was the cleaner fix than retrofitting auth. Users on `>= 0.8.0` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-m69w-p7m4-585j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45667
- https://github.com/open-webui/open-webui/commit/e5035ea31e179977e805a7032c979ff59a71860a
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.0
