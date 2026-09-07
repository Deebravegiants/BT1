# [M] Casdoor Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rwcp-qrwg-56cg
CVE: CVE-2023-34927
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-rwcp-qrwg-56cg
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
Casdoor v1.331.0 and below was discovered to contain a Cross-Site Request Forgery (CSRF) in the endpoint `/api/set-password`. This vulnerability allows attackers to arbitrarily change the victim user's password via supplying a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34927
- https://github.com/casdoor/casdoor/issues/1531
- https://casdoor.org
- https://gist.github.com/omriman067/4e90a3a4ffa40984f011d8777a995469
- https://github.com/casdoor/casdoor
