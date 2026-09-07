# [M] Next.js: null origin can bypass Server Actions CSRF checks

## Summary
Severity: Medium
Advisory: GHSA-mq59-m269-xvcx
CVE: CVE-2026-27978
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-mq59-m269-xvcx
Type: github-advisory

## Affected
- npm: `next` — affected >=16.0.1 <16.1.7

## Details
## Summary
`origin: null` was treated as a "missing" origin during Server Action CSRF validation. As a result, requests from opaque contexts (such as sandboxed iframes) could bypass origin verification instead of being validated as cross-origin requests.

## Impact
An attacker could induce a victim browser to submit Server Actions from a sandboxed context, potentially executing state-changing actions with victim credentials (CSRF).

## Patches
Fixed by treating `'null'` as an explicit origin value and enforcing host/origin checks unless `'null'` is explicitly allowlisted in `experimental.serverActions.allowedOrigins`.  

## Workarounds
If upgrade is not immediately possible:
- Add CSRF tokens for sensitive Server Actions.
- Prefer `SameSite=Strict` on sensitive auth cookies.
- Do not allow `'null'` in `serverActions.allowedOrigins` unless intentionally required and additionally protected.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-mq59-m269-xvcx
- https://nvd.nist.gov/vuln/detail/CVE-2026-27978
- https://github.com/vercel/next.js/commit/a27a11d78e748a8c7ccfd14b7759ad2b9bf097d8
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v16.1.7
