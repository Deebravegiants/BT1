# [H] JLSEC-2026-50

## Summary
Severity: High
Advisory: JLSEC-2026-50
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-50
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.8.0+0

## Details
Incorrect control of environment variables in PostgreSQL PL/Perl allows an unprivileged database user to change sensitive process environment variables (e.g. PATH).  That often suffices to enable arbitrary code execution, even if the attacker lacks a database server operating system user.  Versions before PostgreSQL 17.1, 16.5, 15.9, 14.14, 13.17, and 12.21 are affected.

## References
- https://github.com/fmora50591/postgresql-env-vuln/blob/main/README.md
- https://lists.debian.org/debian-lts-announce/2024/11/msg00011.html
- https://security.netapp.com/advisory/ntap-20250110-0003/
- https://www.postgresql.org/support/security/CVE-2024-10979/
