# [M] Suite CRM v7.14.2 - SSRF

## Summary
Severity: Medium
Advisory: BIT-suitecrm-2023-6388
Aliases: CVE-2023-6388
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2023-6388
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=7.14.2 <7.14.3

## Details
Suite CRM version 7.14.2 allows making arbitrary HTTP requests through

the vulnerable server. This is possible because the application is vulnerable

to SSRF.

## References
- https://fluidattacks.com/advisories/leon/
- https://github.com/salesagility/SuiteCRM/
- https://nvd.nist.gov/vuln/detail/CVE-2023-6388
