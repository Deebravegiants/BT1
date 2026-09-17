# [M] ALPINE-CVE-2022-30783

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-30783
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30783
Type: osv

## Affected
- Alpine:v3.16: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.17: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.18: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.19: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.20: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.21: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.22: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.23: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.24: `ntfs-3g` — affected >=0 <2022.5.17-r0

## Details
An invalid return code in fuse_kern_mount enables intercepting of libfuse-lite protocol traffic between NTFS-3G and the kernel in NTFS-3G through 2021.8.22 when using libfuse-lite.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30783
