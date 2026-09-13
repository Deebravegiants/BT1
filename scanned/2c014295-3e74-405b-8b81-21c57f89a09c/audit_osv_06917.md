# [M] MongoDB Aggregation Command Invariant Assertion Failure Leading to Process Termination

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13073
Aliases: CVE-2026-13073
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13073
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.28

## Details
An authenticated user with read-only privileges can cause the mongod process to terminate abnormally by issuing a crafted aggregation command, resulting in denial of service for all connected clients until the process is restarted. The issue stems from an internal engine selection inconsistency triggered by a specific combination of aggregation options.

## References
- https://jira.mongodb.org/browse/SERVER-128512
- https://nvd.nist.gov/vuln/detail/CVE-2026-13073
