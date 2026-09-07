# [H] Unexpected server crash in Next.js.

## Summary
Severity: High
Advisory: GHSA-25mp-g6fv-mqxx
CVE: CVE-2021-43803
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-07
Source: https://github.com/advisories/GHSA-25mp-g6fv-mqxx
Type: github-advisory

## Affected
- npm: `next` — affected >=12.0.0 <12.0.5
- npm: `next` — affected >=0.9.9 <11.1.3

## Details
Next.js is a React framework. In versions of Next.js prior to 12.0.5 or 11.1.3, invalid or malformed URLs could lead to a server crash. In order to be affected by this issue, the deployment must use Next.js versions above 11.1.0 and below 12.0.5, Node.js above 15.0.0, and next start or a custom server. Deployments on Vercel are not affected, along with similar environments where invalid requests are filtered before reaching Next.js. Versions 12.0.5 and 11.1.3 contain patches for this issue. Note that prior version 0.9.9 package `next` hosted a different utility (0.4.1 being the latest version of that codebase), and this advisory does not apply to those versions.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-25mp-g6fv-mqxx
- https://nvd.nist.gov/vuln/detail/CVE-2021-43803
- https://github.com/vercel/next.js/pull/32080
- https://github.com/vercel/next.js/commit/6d98b4fb4315dec1badecf0e9bdc212a4272b264
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v11.1.3
- https://github.com/vercel/next.js/releases/v12.0.5
