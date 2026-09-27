# [H] rttys SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-54q4-74p3-mgcw
CVE: CVE-2022-38867
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-54q4-74p3-mgcw
Type: github-advisory

## Affected
- Go: `github.com/zhaojh329/rttys` — affected >=4.0.0

## Details
SQL Injection vulnerability in rttys versions 4.0.0, 4.0.1, and 4.0.2 in api.go, allows attackers to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38867
- https://github.com/zhaojh329/rttys/issues/117
- https://github.com/zhaojh329/rttys
- https://github.com/zhaojh329/rttys/blob/v4.4.1/api.go#L295
