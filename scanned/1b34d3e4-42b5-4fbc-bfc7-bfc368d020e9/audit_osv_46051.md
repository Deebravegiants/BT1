# [H] JLSEC-2026-608

## Summary
Severity: High
Advisory: JLSEC-2026-608
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-608
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=16.0.0+0 <16.14.0+0

## Details
SQL injection in PostgreSQL logical replication ALTER SUBSCRIPTION ... REFRESH PUBLICATION allows a subscriber table creator to execute arbitrary SQL with the subscription's publication-side credentials.  The attack takes effect at the next REFRESH PUBLICATION.  Within major versions 16, 17, and 18, minor versions before PostgreSQL 18.4, 17.10, and 16.14 are affected.  Versions before PostgreSQL 16 are unaffected.

## References
- https://www.postgresql.org/support/security/CVE-2026-6638/
