# [M] Next.js: HTTP request smuggling in rewrites

## Summary
Severity: Medium
Advisory: GHSA-ggv3-7p47-pfv8
CVE: CVE-2026-29057
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-ggv3-7p47-pfv8
Type: github-advisory

## Affected
- npm: `next` — affected >=16.0.0-beta.0 <16.1.7
- npm: `next` — affected >=9.5.0 <15.5.13

## Details
## Summary
When Next.js rewrites proxy traffic to an external backend, a crafted `DELETE`/`OPTIONS` request using `Transfer-Encoding: chunked` could trigger request boundary disagreement between the proxy and backend. This could allow request smuggling through rewritten routes.

## Impact
An attacker could smuggle a second request to unintended backend routes (for example, internal/admin endpoints), bypassing assumptions that only the configured rewrite destination/path is reachable. This does not impact applications hosted on providers that handle rewrites at the CDN level, such as Vercel. 

## Patches
The vulnerability originated in an upstream library vendored by Next.js. It is fixed by updating that dependency’s behavior so `content-length: 0` is added only when both `content-length` and `transfer-encoding` are absent, and `transfer-encoding` is no longer removed in that code path.

## Workarounds
If upgrade is not immediately possible:
- Block chunked `DELETE`/`OPTIONS` requests on rewritten routes at your edge/proxy.
- Enforce authentication/authorization on backend routes per our [security guidance](https://nextjs.org/docs/app/guides/data-security).

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-ggv3-7p47-pfv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-29057
- https://github.com/vercel/next.js/commit/dc98c04f376c6a1df76ec3e0a2d07edf4abdabd6
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.13
- https://github.com/vercel/next.js/releases/tag/v16.1.7
