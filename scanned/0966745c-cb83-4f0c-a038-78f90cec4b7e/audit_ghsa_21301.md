# [M] Hashicorp Boundary vulnerable to clickjacking

## Summary
Severity: Medium
Advisory: GHSA-xqv2-3vvq-qg6r
CVE: CVE-2022-36182
CWE: CWE-1021
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-27
Source: https://github.com/advisories/GHSA-xqv2-3vvq-qg6r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/boundary` — affected >=0

## Details
Hashicorp Boundary is vulnerable to Clickjacking which allow for the interception of login credentials, re-direction of users to malicious sites, or causing users to perform malicious actions on the site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36182
- https://github.com/hashicorp/boundary
- https://owasp.org/www-community/attacks/Clickjacking
- https://packetstormsecurity.com/files/168654/Hashicorp-Boundary-Clickjacking.html
