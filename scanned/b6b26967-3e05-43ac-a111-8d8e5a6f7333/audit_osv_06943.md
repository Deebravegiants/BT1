# [H] Unbounded recursion in BSONColumn interleaved-reference causes pre-auth stack overflow

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9740
Aliases: CVE-2026-9740
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9740
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
A vulnerability in MongoDB Server's BSON validation logic allows an unauthenticated user to crash the mongod process by sending a specially crafted message. The BSON validator's handling of certain nested binary data structures permits uncontrolled mutual recursion between validation functions, where each re-entry resets internal depth tracking.

## References
- https://jira.mongodb.org/browse/SERVER-125063
- https://nvd.nist.gov/vuln/detail/CVE-2026-9740
