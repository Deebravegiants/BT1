# [H] DataEase: Stored SQL Injection Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-45535
Aliases: GHSA-pv23-p64m-4pxf
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-45535
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.23, DataEase SQL-type datasets store attacker-controlled SQL variable defaultValue entries such as ${var} and SqlparserUtils.handleVariableDefaultValue() inserts them with String.replace() without escaping or parameterization, causing stored SQL injection whenever a user with dataset read permission accesses the dataset. This issue is fixed in version 2.10.23.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45535.json
- https://github.com/dataease/dataease/security/advisories/GHSA-pv23-p64m-4pxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45535
- https://github.com/dataease/dataease/commit/22930a493d900fe3d8084b3dd4c0125abdb2a847
