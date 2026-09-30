# [H] Next.js has a Middleware / Proxy bypass through dynamic route parameter injection

## Summary
Severity: High
Advisory: GHSA-492v-c6pp-mqqv
CVE: CVE-2026-44574
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-492v-c6pp-mqqv
Type: github-advisory

## Affected
- npm: `next` — affected >=15.4.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

Applications that rely on middleware to protect dynamic routes can be vulnerable to authorization bypass. In affected deployments, specially crafted query parameters can alter the dynamic route value seen by the page while leaving the visible path unchanged, which can allow protected content to be rendered without passing the expected middleware check.

### Fix

We now only honor internal route-parameter normalization in trusted routing flows and ignore externally supplied parameter encodings that should never have been accepted from ordinary requests.

### Workarounds

If you cannot upgrade immediately, enforce authorization in route or page logic instead of relying solely on middleware path matching.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-492v-c6pp-mqqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44574
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
