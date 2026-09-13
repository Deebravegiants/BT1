# [H] $rankFusion and $scoreFusion Unbounded Memory Allocation During Error Suggestion Generation

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13075
Aliases: CVE-2026-13075
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13075
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user can cause the mongod process to be terminated by the operating system under memory pressure via the $rankFusion and $scoreFusion aggregation stages. The issue originates in the server's error-handling path and requires the ability to run aggregation queries.

## References
- https://jira.mongodb.org/browse/SERVER-128316
- https://nvd.nist.gov/vuln/detail/CVE-2026-13075
