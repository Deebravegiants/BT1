# [H] PostgreSQL psql COPY FROM STDIN early failure processes data lines as psql commands

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6464
Aliases: CVE-2026-6464
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6464
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Untrusted data inclusion in PostgreSQL psql COPY may allow a server administrator to elicit execution of data lines as psql commands, via error injection.  If the "COPY FROM STDIN" or "\copy FROM STDIN" command fails before the server indicates that it awaits input rows, psql processes the in-line data rows as psql commands.  "COPY FROM" with a filename is unaffected.  The server administrator has no inherent control over the data rows, so a complete attack requires the attacker to separately acquire control of both the server and the data rows.  Alternatively, an attacker controlling data rows alone might complete an attack through a coincidental error that they don't control.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6464
- https://www.postgresql.org/support/security/CVE-2026-6464/
