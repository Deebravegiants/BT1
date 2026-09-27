# [M] PostgreSQL fails to check type USAGE privilege

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-6470
Aliases: CVE-2026-6470
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6470
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Missing authorization in PostgreSQL DDL commands allows an object creator to achieve denial of service against ALTER and DROP of the type, via creating a dependency on the type.  Many DDL operations did check the privilege, but assigning a range subtype and referencing the type from an SQL expression did not.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6470
- https://www.postgresql.org/support/security/CVE-2026-6470/
