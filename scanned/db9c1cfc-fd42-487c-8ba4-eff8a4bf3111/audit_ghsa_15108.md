# [H] @urql/next Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-qhjf-hm5j-335w
CVE: CVE-2024-24556
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-qhjf-hm5j-335w
Type: github-advisory

## Affected
- npm: `@urql/next` — affected >=0 <1.1.1

## Details
## impact

The `@urql/next` package is vulnerable to XSS. To exploit this an attacker would need to ensure that the response returns `html` tags and that the web-application is using streamed responses (non-RSC). This vulnerability is due to improper escaping of html-like characters in the response-stream.

To fix this vulnerability upgrade to version 1.1.1

## References
- https://github.com/urql-graphql/urql/security/advisories/GHSA-qhjf-hm5j-335w
- https://nvd.nist.gov/vuln/detail/CVE-2024-24556
- https://github.com/urql-graphql/urql/commit/4b7011b70d5718728ff912d02a4dbdc7f703540d
- https://github.com/urql-graphql/urql
