# [H] SaToken authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-w9vh-hv5g-7wmr
CVE: CVE-2023-43961
CWE: CWE-287, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-w9vh-hv5g-7wmr
Type: github-advisory

## Affected
- Maven: `cn.dev33:sa-token-core` — affected >=0 <1.36.0

## Details
An issue in Dromara SaToken version 1.3.50RC and before when using Spring dynamic controllers, a specially crafted request may cause an authentication bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43961
- https://github.com/dromara/Sa-Token/issues/511
- https://github.com/dromara/Sa-Token
