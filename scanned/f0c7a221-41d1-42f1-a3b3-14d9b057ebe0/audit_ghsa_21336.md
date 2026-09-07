# [H] Dapr Dashboard vulnerable to Incorrect Access Control

## Summary
Severity: High
Advisory: GHSA-2w6m-q946-399r
CVE: CVE-2022-38817
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-04
Source: https://github.com/advisories/GHSA-2w6m-q946-399r
Type: github-advisory

## Affected
- Go: `github.com/dapr/dashboard` — affected >=0.1.0

## Details
Dapr Dashboard v0.1.0 through v0.10.0 is vulnerable to Incorrect Access Control that allows attackers to obtain sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38817
- https://github.com/dapr/dashboard/issues/222
- https://github.com/dapr/dashboard
