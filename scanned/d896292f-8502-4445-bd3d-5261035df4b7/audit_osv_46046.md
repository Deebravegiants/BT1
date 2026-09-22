# [H] JLSEC-2026-603

## Summary
Severity: High
Advisory: JLSEC-2026-603
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-603
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Symlink following in PostgreSQL `pg_basebackup` plain format and in `pg_rewind` allows an origin superuser to overwrite local files, e.g. `/var/lib/postgres/.bashrc`, that hijack the operating system account.  It will remain the case that starting the server after these commands implicitly trusts the origin superuser, due to features like `shared_preload_libraries`.  Hence, the attack has practical implications only if one takes relevant action between these commands and server start, like moving the files to a different VM or snapshotting the VM.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2026-6475/
