# [H] Transaction Command Insufficient Input Validation Leading to Process Termination

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13058
Aliases: CVE-2026-13058
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13058
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user with basic write privileges can cause the mongod process to terminate abnormally by sending a crafted transaction command with an incomplete set of required fields. The issue stems from inconsistent validation across related transaction command parameters, resulting in a fatal internal invariant failure and denial of service.

## References
- https://jira.mongodb.org/browse/SERVER-127661
- https://nvd.nist.gov/vuln/detail/CVE-2026-13058
