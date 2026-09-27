# [H] SuiteCRM v4 API Excessive log data DOS

## Summary
Severity: High
Advisory: BIT-suitecrm-2024-36416
Aliases: CVE-2024-36416, GHSA-jrpp-22g3-2j77
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36416
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. Prior to versions 7.14.4 and 8.6.1, a deprecated v4 API example with no log rotation allows denial of service by logging excessive data. Versions 7.14.4 and 8.6.1 contain a fix for this issue.

## References
- https://github.com/salesagility/SuiteCRM/security/advisories/GHSA-jrpp-22g3-2j77
- https://docs.suitecrm.com/admin/releases/7.14.x/
- https://github.com/kva55/CVE-2024-36416
- https://nvd.nist.gov/vuln/detail/CVE-2024-36416
