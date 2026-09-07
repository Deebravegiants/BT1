# [C] SQLinjection in falcon-plus

## Summary
Severity: Critical
Advisory: GHSA-76j4-gggq-7rg9
CVE: CVE-2022-26245
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-28
Source: https://github.com/advisories/GHSA-76j4-gggq-7rg9
Type: github-advisory

## Affected
- Go: `github.com/open-falcon/falcon-plus` — affected >=0

## Details
Falcon-plus v0.3 was discovered to contain a SQL injection vulnerability via the parameter grpName in /config/service/host.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26245
- https://github.com/open-falcon/falcon-plus/issues/951
- github.com/open-falcon/falcon-plus
