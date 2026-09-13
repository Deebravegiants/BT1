# [H] PostgreSQL pg_basebackup and pg_rewind can overwrite unrelated files of origin superuser choice

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6475
Aliases: CVE-2026-6475
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6475
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Symlink following in PostgreSQL pg_basebackup plain format and in pg_rewind allows an origin superuser to overwrite local files, e.g. /var/lib/postgres/.bashrc, that hijack the operating system account.  It will remain the case that starting the server after these commands implicitly trusts the origin superuser, due to features like shared_preload_libraries.  Hence, the attack has practical implications only if one takes relevant action between these commands and server start, like moving the files to a different VM or snapshotting the VM.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6475
- https://www.postgresql.org/support/security/CVE-2026-6475/
