# [H] ALPINE-CVE-2021-41072

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41072
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-09-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41072
Type: osv

## Affected
- Alpine:v3.14: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.15: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.16: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.17: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.18: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.19: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.20: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.21: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.22: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.23: `squashfs-tools` — affected >=0 <4.5-r1
- Alpine:v3.24: `squashfs-tools` — affected >=0 <4.5-r1

## Details
squashfs_opendir in unsquash-2.c in Squashfs-Tools 4.5 allows Directory Traversal, a different vulnerability than CVE-2021-40153. A squashfs filesystem that has been crafted to include a symbolic link and then contents under the same filename in a filesystem can cause unsquashfs to first create the symbolic link pointing outside the expected directory, and then the subsequent write operation will cause the unsquashfs process to write through the symbolic link elsewhere in the filesystem.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41072
