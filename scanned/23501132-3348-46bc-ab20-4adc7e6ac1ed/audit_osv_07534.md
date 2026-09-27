# [H] BIT-suitecrm-2021-45041

## Summary
Severity: High
Advisory: BIT-suitecrm-2021-45041
Aliases: CVE-2021-45041
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2021-45041
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=0 <7.12.2, >=8.0.0

## Details
SuiteCRM before 7.12.2 and 8.x before 8.0.1 allows authenticated SQL injection via the Tooltips action in the Project module, involving resource_id and start_date.

## References
- https://docs.suitecrm.com/8.x/admin/releases/8.0/
- https://docs.suitecrm.com/admin/releases/7.12.x/
- https://github.com/manuelz120/CVE-2021-45041
- https://nvd.nist.gov/vuln/detail/CVE-2021-45041
