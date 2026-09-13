# [C] MongoDB Server may access non-initialized region of memory leading to unexpected behaviour

## Summary
Severity: Critical
Advisory: BIT-mongodb-2024-8654
Aliases: CVE-2024-8654
Ecosystem: Bitnami
Published: 2025-09-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-8654
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=6.0.0 <6.0.15

## Details
MongoDB Server may access non-initialized region of memory leading to unexpected behaviour when zero arguments are called in internal aggregation stage. This issue affected MongoDB Server v6.0 version 6.0.3.

## References
- https://jira.mongodb.org/browse/SERVER-71477
- https://nvd.nist.gov/vuln/detail/CVE-2024-8654
- https://security.netapp.com/advisory/ntap-20250516-0008/
