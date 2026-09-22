# [M] Malformed KMIP response may result in access violation

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-12657
Aliases: CVE-2025-12657
Ecosystem: Bitnami
Published: 2025-12-13
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-12657
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.10

## Details
The KMIP response parser built into mongo binaries is overly tolerant of certain malformed packets, and may parse them into invalid objects. Later reads of this object can result in read access violations.

## References
- https://jira.mongodb.org/browse/SERVER-101230
- https://nvd.nist.gov/vuln/detail/CVE-2025-12657
