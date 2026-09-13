# [M] OpenClaw has unbounded memory growth in Zalo webhook via query-string key churn (unauthenticated DoS)

## Summary
Severity: Medium
Advisory: GHSA-wr6m-jg37-68xh
CVE: CVE-2026-32066
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-wr6m-jg37-68xh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
Unauthenticated requests to a reachable Zalo webhook endpoint could trigger unbounded in-memory key growth by varying query strings on the same valid webhook route.

### Impact
An attacker could cause memory pressure and potential process instability or OOM, degrading availability.

### Fix
Webhook security tracking now normalizes keys to matched webhook path semantics (query excluded) and bounds/prunes tracking state to prevent unbounded growth.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wr6m-jg37-68xh
- https://github.com/openclaw/openclaw
