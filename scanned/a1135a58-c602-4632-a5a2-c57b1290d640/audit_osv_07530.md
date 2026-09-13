# [M] BIT-suitecrm-2021-41595

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2021-41595
Aliases: CVE-2021-41595
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2021-41595
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=7.11.0 <7.11.22

## Details
SuiteCRM before 7.10.33 and 7.11.22 allows information disclosure via Directory Traversal. An attacker can partially include arbitrary files via the file_name parameter of the Step3 import functionality.

## References
- https://docs.suitecrm.com/admin/releases/7.10.x/#_7_10_33
- https://docs.suitecrm.com/admin/releases/7.11.x/#_7_11_22
- https://github.com/ach-ing/cves/blob/main/CVE-2021-41595.md
- https://github.com/salesagility/SuiteCRM
- https://nvd.nist.gov/vuln/detail/CVE-2021-41595
