# [H] Buffer Overflow in gitea

## Summary
Severity: High
Advisory: GHSA-9f8c-pfvv-p4gm
CVE: CVE-2021-3382
CWE: CWE-787
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-9f8c-pfvv-p4gm
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=1.9.0 <1.13.2

## Details
Stack buffer overflow vulnerability in gitea 1.9.0 through 1.13.1 allows remote attackers to cause a denial of service (crash) via vectors related to a file path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3382
- https://github.com/go-gitea/gitea/pull/14390
- https://github.com/go-gitea/gitea
