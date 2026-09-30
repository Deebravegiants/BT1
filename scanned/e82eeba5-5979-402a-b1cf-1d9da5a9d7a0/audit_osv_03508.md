# [M] ALPINE-CVE-2026-2340

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-2340
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2340
Type: osv

## Affected
- Alpine:v3.23: `samba` — affected >=4.1.0 <4.22.10-r0
- Alpine:v3.24: `samba` — affected >=4.1.0 <4.23.8-r0

## Details
A flaw was found in Samba’s vfs_worm module. The module is intended to provide write-once, read-many (WORM) protections by preventing modification of files after a configurable grace period. Due to insufficient validation during rename operations, an authenticated user with write access to a share could overwrite a protected file by renaming a newly created file over the existing WORM-protected file.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2340
