# [H] ALPINE-CVE-2021-40153

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-40153
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40153
Type: osv

## Affected
- Alpine:v3.11: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.12: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.13: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.14: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.15: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.16: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.17: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.18: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.19: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.20: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.21: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.22: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.23: `squashfs-tools` — affected >=0 <4.5-r0
- Alpine:v3.24: `squashfs-tools` — affected >=0 <4.5-r0

## Details
squashfs_opendir in unsquash-1.c in Squashfs-Tools 4.5 stores the filename in the directory entry; this is then used by unsquashfs to create the new file during the unsquash. The filename is not validated for traversal outside of the destination directory, and thus allows writing to locations outside of the destination.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40153
