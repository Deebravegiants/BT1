# [H] Phachon mm-wiki Cross Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-f6xp-59jq-r35c
CVE: CVE-2020-19278
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-f6xp-59jq-r35c
Type: github-advisory

## Affected
- Go: `github.com/phachon/mm-wiki` — affected >=0

## Details
Cross Site Request Forgery vulnerability found in Phachon mm-wiki v.0.1.2 allows a remote attacker to execute arbitrary code via the system/user/save parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19278
- https://github.com/phachon/mm-wiki/issues/68
- https://github.com/phachon/mm-wiki
- https://imgur.com/EABvnwz
