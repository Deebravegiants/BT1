# [M] LocalAI cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jhvf-7c85-3c9g
CVE: CVE-2024-3135
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-01
Source: https://github.com/advisories/GHSA-jhvf-7c85-3c9g
Type: github-advisory

## Affected
- Go: `github.com/go-skynet/LocalAI` — affected >=0

## Details
A Cross-Site Request Forgery (CSRF) vulnerability exists in the mudler/localai application, allowing attackers to craft malicious webpages that, when visited by a victim, perform unauthorized actions on the victim's local LocalAI instance without their consent. This vulnerability enables attackers to exhaust system resources, consume credits, and fill disk space by making numerous resource-intensive API calls, such as generating images or uploading files. The vulnerability stems from the application's acceptance of simple request content-types without requiring CSRF tokens or implementing other CSRF mitigation measures. Successful exploitation does not require network access to the vulnerable LocalAI environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3135
- https://github.com/mudler/LocalAI
- https://huntr.com/bounties/7afdc4d3-4b68-45ea-96d0-cf9ed3712ae8
