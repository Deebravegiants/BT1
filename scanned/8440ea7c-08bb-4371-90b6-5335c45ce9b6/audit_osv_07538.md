# [H] BIT-suitecrm-2022-45185

## Summary
Severity: High
Advisory: BIT-suitecrm-2022-45185
Aliases: CVE-2022-45185
Ecosystem: Bitnami
Published: 2025-04-16
Source: https://osv.dev/vulnerability/BIT-suitecrm-2022-45185
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=7.12.7

## Details
An issue was discovered in SuiteCRM 7.12.7. Authenticated users can use CRM functions to upload malicious files. Then, deserialization can be used to achieve code execution.

## References
- https://docs.suitecrm.com/admin/releases/7.12.x/
- https://github.com/Orange-Cyberdefense/CVE-repository/
- https://github.com/Orange-Cyberdefense/CVE-repository/blob/master/PoCs/poc_SuiteCRM.py
- https://nvd.nist.gov/vuln/detail/CVE-2022-45185
