# [M] @perfood/couch-auth has a host header injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qw8v-34ww-6q9p
CVE: CVE-2025-70948
CWE: CWE-644, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-qw8v-34ww-6q9p
Type: github-advisory

## Affected
- npm: `@perfood/couch-auth` — affected >=0

## Details
A host header injection vulnerability in the mailer component of @perfood/couch-auth v0.26.0 allows attackers to obtain reset tokens and execute an account takeover via spoofing the HTTP Host header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70948
- https://gist.github.com/0xHunterr/38aab644874ca9f4646524c5b01cfe5e
- https://github.com/perfood/couch-auth
- https://www.npmjs.com/package/@perfood/couch-auth
