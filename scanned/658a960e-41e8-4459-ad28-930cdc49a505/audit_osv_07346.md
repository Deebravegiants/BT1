# [H] PostgreSQL stack buffer overflow in argument match writes 0x0 and 0x1 to server memory

## Summary
Severity: High
Advisory: BIT-postgresql-2026-14679
Aliases: CVE-2026-14679
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14679
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Stack buffer overflow in PostgreSQL argument name matching allows an object creator to achieve unknown impacts via OUT parameter count.  The attack can write only 0x0 and 0x1 bytes.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14679
- https://www.postgresql.org/support/security/CVE-2026-14679/
