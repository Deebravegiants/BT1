# [H] Next.js has a Middleware / Proxy bypass in Pages Router applications using i18n

## Summary
Severity: High
Advisory: GHSA-36qx-fr4f-26g5
CVE: CVE-2026-44573
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-36qx-fr4f-26g5
Type: github-advisory

## Affected
- npm: `next` — affected >=12.2.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

Applications using the Pages Router with `i18n` configured and middleware/proxy-based authorization can allow unauthorized access to protected page data through locale-less `/_next/data/<buildId>/<page>.json` requests. In affected configurations, middleware does not run for the unprefixed data route, allowing an attacker to retrieve SSR JSON for protected pages without passing the intended authorization checks.

### Fix
The matcher logic was updated to perform the same match as it would on a non-i18n data route.

### Workarounds

If you cannot upgrade immediately, enforce authorization in the page's server-side data path instead of relying solely on middleware.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-36qx-fr4f-26g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44573
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
