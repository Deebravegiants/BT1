# [H] PostgreSQL PL/Perl environment variable changes execute arbitrary code

## Summary
Severity: High
Advisory: BIT-postgresql-2024-10979
Aliases: CVE-2024-10979
Ecosystem: Bitnami
Published: 2024-11-16
Source: https://osv.dev/vulnerability/BIT-postgresql-2024-10979
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=17.0.0 <17.1.0

## Details
Incorrect control of environment variables in PostgreSQL PL/Perl allows an unprivileged database user to change sensitive process environment variables (e.g. PATH).  That often suffices to enable arbitrary code execution, even if the attacker lacks a database server operating system user.  Versions before PostgreSQL 17.1, 16.5, 15.9, 14.14, 13.17, and 12.21 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2024-10979/
- https://github.com/fmora50591/postgresql-env-vuln/blob/main/README.md
- https://security.netapp.com/advisory/ntap-20250110-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2024-10979
- https://lists.debian.org/debian-lts-announce/2024/11/msg00011.html
