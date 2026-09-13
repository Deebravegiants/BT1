# [H] BIT-processmaker-2020-13525

## Summary
Severity: High
Advisory: BIT-processmaker-2020-13525
Aliases: CVE-2020-13525
Ecosystem: Bitnami
Published: 2023-11-06
Source: https://osv.dev/vulnerability/BIT-processmaker-2020-13525
Type: osv

## Affected
- Bitnami: `processmaker` — affected >=3.4.11

## Details
The sort parameter in the download page /sysworkflow/en/neoclassic/reportTables/reportTables_Ajax is vulnerable to SQL injection in ProcessMaker 3.4.11. A specially crafted HTTP request can cause an SQL injection. An attacker can make an authenticated HTTP request to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1126
