# [M] @koa/router has an Access Control Bypass

## Summary
Severity: Medium
Advisory: GHSA-47p6-69vm-vw6v
CVE: CVE-2026-9495
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-47p6-69vm-vw6v
Type: github-advisory

## Affected
- npm: `@koa/router` — affected >=14.0.0 <15.0.0

## Details
Versions of the package @koa/router from 14.0.0 and before 15.0.0 are vulnerable to Access Control Bypass due to the middleware being silently dropped from the execution chain when the router prefix contains path parameters. Depending on what the skipped middleware was supposed to protect, an attacker could bypass authentication and authorization, evade rate limiting or bypass input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9495
- https://github.com/koajs/router/issues/202
- https://github.com/koajs/router/pull/206
- https://github.com/koajs/router/commit/d53e17f284557b1f417946f9807ee52290c3c759
- https://github.com/koajs/router
- https://security.snyk.io/vuln/SNYK-JS-KOAROUTER-12215044
