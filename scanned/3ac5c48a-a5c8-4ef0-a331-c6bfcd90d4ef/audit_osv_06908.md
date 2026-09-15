# [M] libmongocrypt Improper Input Validation Leading to Process Termination

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13063
Aliases: CVE-2026-13063
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13063
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user with standard read/write privileges can cause the mongod process to terminate due to an out-of-memory condition by sending a crafted aggregation command. MongoDB's libmongocrypt library insufficiently validates payload-supplied values, which can result in an excessively large memory allocation.

## References
- https://jira.mongodb.org/browse/SERVER-127737
- https://nvd.nist.gov/vuln/detail/CVE-2026-13063
