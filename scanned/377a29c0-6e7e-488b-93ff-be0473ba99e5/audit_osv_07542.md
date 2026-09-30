# [H] Suite CRM v7.14.2 - RCE via Local File Inclusion

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-1644
Aliases: CVE-2024-1644
Ecosystem: Bitnami
Published: 2025-01-01
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-1644
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=7.14.2 <7.14.3

## Details
Suite CRM version 7.14.2 allows including local php files. This is possible

because the application is vulnerable to LFI.

## References
- https://fluidattacks.com/advisories/silva/
- https://github.com/salesagility/SuiteCRM/
- https://nvd.nist.gov/vuln/detail/CVE-2024-1644
