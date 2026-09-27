# [M] Certain Queries with Duplicate _id Fields May Cause MongoDB Server to Crash

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-7259
Aliases: CVE-2025-7259
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-7259
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.1.0 <8.2.0

## Details
An authorized user can issue queries with duplicate _id fields, that leads to unexpected behavior in MongoDB Server, which may result to crash. This issue can only be triggered by authorized users and cause Denial of Service. This issue affects MongoDB Server v8.1 version 8.1.0.

## References
- https://jira.mongodb.org/browse/SERVER-102693
- https://nvd.nist.gov/vuln/detail/CVE-2025-7259
