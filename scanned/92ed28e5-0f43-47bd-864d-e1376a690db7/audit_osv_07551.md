# [H] SuiteCRM Improper Control of Filename for Include Statement in PHP and Unrestricted Upload of File with Dangerous content leads to authenticated remote code execution

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-36415
Aliases: CVE-2024-36415, GHSA-c82f-58jv-jfrh
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36415
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. Prior to versions 7.14.4 and 8.6.1, a vulnerability in uploaded file verification in products allows for remote code execution. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-c82f-58jv-jfrh
- https://nvd.nist.gov/vuln/detail/CVE-2024-36415
