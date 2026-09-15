# [H] CouchAuth host header injection vulnerability leaks the password reset token

## Summary
Severity: High
Advisory: GHSA-fqh6-6h6c-366m
CVE: CVE-2023-39655
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-fqh6-6h6c-366m
Type: github-advisory

## Affected
- npm: `@perfood/couch-auth` — affected >=0

## Details
A host header injection vulnerability exists in the NPM package @perfood/couch-auth versions <= 0.20.0. By sending a specially crafted host header in the forgot password request, it is possible to send password reset links to users which, once clicked, lead to an attacker-controlled server and thus leak the password reset token. This may allow an attacker to reset other users' passwords and take over their accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39655
- https://github.com/dub-flow/vulnerability-research/tree/main/CVE-2023-39655
- https://github.com/perfood/couch-auth
- https://www.npmjs.com/package/%40perfood/couch-auth
