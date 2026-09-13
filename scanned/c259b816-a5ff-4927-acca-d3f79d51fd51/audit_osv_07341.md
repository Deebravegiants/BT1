# [H] PostgreSQL ctid type confusion in selectivity estimator discloses derivative of arbitrary read

## Summary
Severity: High
Advisory: BIT-postgresql-2026-14668
Aliases: CVE-2026-14668
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14668
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Type confusion regarding input of PostgreSQL ctid data type selectivity estimator allows an object creator to view a calculation derived from the value of an arbitrary 4-byte span of memory, via a chosen non-ctid input.  While the calculation loses precision, substantial memory value recovery appears possible.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14668
- https://www.postgresql.org/support/security/CVE-2026-14668/
