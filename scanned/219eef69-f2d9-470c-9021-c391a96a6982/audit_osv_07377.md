# [H] BIT-processmaker-2020-13526

## Summary
Severity: High
Advisory: BIT-processmaker-2020-13526
Aliases: CVE-2020-13526
Ecosystem: Bitnami
Published: 2023-11-06
Source: https://osv.dev/vulnerability/BIT-processmaker-2020-13526
Type: osv

## Affected
- Bitnami: `processmaker` — affected >=3.4.11

## Details
SQL injection vulnerability exists in the handling of sort parameters in ProcessMaker 3.4.11. A specially crafted HTTP request can cause an SQL injection. The reportTables_Ajax and clientSetupAjax pages are vulnerable to SQL injection in the sort parameter.An attacker can make an authenticated HTTP request to trigger these vulnerabilities.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1126
