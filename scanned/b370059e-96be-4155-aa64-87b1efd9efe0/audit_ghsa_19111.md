# [M] Better Auth URL parameter HTML Injection (Reflected Cross-Site scripting)

## Summary
Severity: Medium
Advisory: GHSA-9x4v-xfq5-m8x5
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-9x4v-xfq5-m8x5
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0.0.2 <1.1.16

## Details
### Summary
The better-auth `/api/auth/error` page was vulnerable to HTML injection, resulting in a reflected cross-site scripting (XSS) vulnerability.

### Details
The value of `error` URL parameter was reflected as HTML on the error page: https://github.com/better-auth/better-auth/blob/05ada0b79dbcac93cc04ceb79b23ca598d07830c/packages/better-auth/src/api/routes/error.ts#L81

### Impact
An attacker who exploited this vulnerability by coercing a user to visit a specially-crafted URL could execute arbitrary JavaScript in the context of the user's browser.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-9x4v-xfq5-m8x5
- https://github.com/better-auth/better-auth/commit/7ae340e2eddad641b7e43d24d37c58a66ce9ddcf
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/blob/05ada0b79dbcac93cc04ceb79b23ca598d07830c/packages/better-auth/src/api/routes/error.ts#L81
