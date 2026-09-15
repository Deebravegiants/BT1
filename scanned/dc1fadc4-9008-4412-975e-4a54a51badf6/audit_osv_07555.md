# [M] SuiteCRM-Core Host Header Injection in /legacy

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2024-36419
Aliases: CVE-2024-36419, GHSA-3323-hjq3-c6vc
Ecosystem: Bitnami
Published: 2024-06-12
Source: https://osv.dev/vulnerability/BIT-suitecrm-2024-36419
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=0 <8.6.1

## Details
SuiteCRM is an open-source Customer Relationship Management (CRM) software application. A vulnerability in versions prior to 8.6.1 allows for Host Header Injection when directly accessing the `/legacy` route. Version 8.6.1 contains a patch for the issue.

## References
- https://github.com/salesagility/SuiteCRM-Core/security/advisories/GHSA-3323-hjq3-c6vc
- https://nvd.nist.gov/vuln/detail/CVE-2024-36419
