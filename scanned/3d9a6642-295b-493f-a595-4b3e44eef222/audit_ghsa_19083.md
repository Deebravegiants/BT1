# [H] Better Auth allows bypassing the trustedOrigins Protection which leads to ATO

## Summary
Severity: High
Advisory: GHSA-vp58-j275-797x
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-vp58-j275-797x
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.1.21

## Details
### Summary

A bypass was discovered in the trustedOrigins validation logic—affecting both absolute URL entries and wildcard domain patterns. This flaw allows an attacker to construct a malicious callbackURL that passes origin checks and triggers an open redirect.

Because redirect endpoints include sensitive tokens (such as password-reset tokens), this vulnerability can enable one-click account takeover if a victim clicks a crafted link.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-vp58-j275-797x
- https://github.com/better-auth/better-auth/commit/b381cac7aafd6aa53ef78b6ab771ebfa24643c80
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/blob/ddebd0358d74376ea64541512d0167dd4377f182/packages/better-auth/src/api/middlewares/origin-check.ts#L53
