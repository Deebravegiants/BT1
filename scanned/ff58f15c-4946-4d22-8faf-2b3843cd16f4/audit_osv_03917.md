# [H] ALPINE-CVE-2026-6475

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6475
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6475
Type: osv

## Affected
- Alpine:v3.20: `postgresql15` — affected >=0 <15.18-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.4-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.4-r0

## Details
Symlink following in PostgreSQL pg_basebackup plain format and in pg_rewind allows an origin superuser to overwrite local files, e.g. /var/lib/postgres/.bashrc, that hijack the operating system account.  It will remain the case that starting the server after these commands implicitly trusts the origin superuser, due to features like shared_preload_libraries.  Hence, the attack has practical implications only if one takes relevant action between these commands and server start, like moving the files to a different VM or snapshotting the VM.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6475
