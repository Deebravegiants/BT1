# [M] PostgreSQL observable response discrepancy with non-default scram_iterations provides user existence oracle

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-14672
Aliases: CVE-2026-14672
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14672
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Observable response discrepancy in PostgreSQL SCRAM authentication allows an unauthenticated user to test the existence of a user via observing the SCRAM iteration count.  This requires the probed user to have a non-default scram_iterations count, because the authentication challenge for a nonexistent user reports the default scram_iterations.  Within major versions 16-18, minor versions before PostgreSQL 18.6, 17.11, and 16.15 are affected.  Versions before PostgreSQL 16 are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14672
- https://www.postgresql.org/support/security/CVE-2026-14672/
