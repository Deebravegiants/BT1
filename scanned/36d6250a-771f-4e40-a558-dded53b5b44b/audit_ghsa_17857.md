# [M] Next.js Improper Middleware Redirect Handling Leads to SSRF

## Summary
Severity: Medium
Advisory: GHSA-4342-x723-ch2f
CVE: CVE-2025-57822
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-4342-x723-ch2f
Type: github-advisory

## Affected
- npm: `next` — affected >=0.9.9 <14.2.32
- npm: `next` — affected >=15.0.0-canary.0 <15.4.7

## Details
A vulnerability in **Next.js Middleware** has been fixed in **v14.2.32** and **v15.4.7**. The issue occurred when request headers were directly passed into `NextResponse.next()`. In self-hosted applications, this could allow Server-Side Request Forgery (SSRF) if certain sensitive headers from the incoming request were reflected back into the response.

All users implementing custom middleware logic in self-hosted environments are strongly encouraged to upgrade and verify correct usage of the `next()` function.

More details at [Vercel Changelog](https://vercel.com/changelog/cve-2025-57822)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-4342-x723-ch2f
- https://nvd.nist.gov/vuln/detail/CVE-2025-57822
- https://github.com/vercel/next.js/commit/9c9aaed5bb9338ef31b0517ccf0ab4414f2093d8
- https://github.com/vercel/next.js
- https://vercel.com/changelog/cve-2025-57822
