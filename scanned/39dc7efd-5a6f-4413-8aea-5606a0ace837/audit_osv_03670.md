# [H] ALPINE-CVE-2026-40706

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-40706
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40706
Type: osv

## Affected
- Alpine:v3.20: `ntfs-3g` — affected >=0 <2026.2.25-r0
- Alpine:v3.21: `ntfs-3g` — affected >=0 <2026.2.25-r0
- Alpine:v3.22: `ntfs-3g` — affected >=0 <2026.2.25-r0
- Alpine:v3.23: `ntfs-3g` — affected >=0 <2026.2.25-r0
- Alpine:v3.24: `ntfs-3g` — affected >=0 <2026.2.25-r0

## Details
In NTFS-3G 2022.10.3 before 2026.2.25, a heap buffer overflow exists in ntfs_build_permissions_posix() in acls.c that allows an attacker to corrupt heap memory in the SUID-root ntfs-3g binary by crafting a malicious NTFS image. The overflow is triggered on the READ path (stat, readdir, open) when processing a security descriptor with multiple ACCESS_DENIED ACEs containing WRITE_OWNER from distinct group SIDs.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40706
