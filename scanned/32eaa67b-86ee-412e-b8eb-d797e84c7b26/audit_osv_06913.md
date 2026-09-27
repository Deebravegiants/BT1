# [H] Queryable Encryption FLE2 Find Payload Missing Input Validation Leading to Resource Exhaustion

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13069
Aliases: CVE-2026-13069
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13069
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user can cause excessive CPU consumption or out-of-memory conditions on a MongoDB server by sending a crafted Queryable Encryption find payload containing an unvalidated field used to control an internal computation loop. The resulting resource exhaustion degrades availability for other operations.

## References
- https://jira.mongodb.org/browse/SERVER-127566
- https://nvd.nist.gov/vuln/detail/CVE-2026-13069
