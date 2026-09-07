# [H] Server-Side Request Forgery in FUXA

## Summary
Severity: High
Advisory: GHSA-9vp3-7qwq-83r9
CVE: CVE-2021-45851
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-17
Source: https://github.com/advisories/GHSA-9vp3-7qwq-83r9
Type: github-advisory

## Affected
- npm: `@frangoteam/fuxa` — affected >=0

## Details
A Server-Side Request Forgery (SSRF) attack in FUXA 1.1.3 can be carried out leading to the obtaining of sensitive information from the server's internal environment and services, often potentially leading to the attacker executing commands on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45851
- https://github.com/frangoteam/FUXA
- https://www.youtube.com/watch?v=JE1Kcq3iJpc
