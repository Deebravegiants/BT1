# [M] ALPINE-CVE-2016-9104

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-9104
Ecosystem: Alpine:v3.10, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9104
Type: osv

## Affected
- Alpine:v3.10: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0
- Alpine:v3.6: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.7: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.8: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.9: `qemu` — affected >=0 <2.8.1-r1

## Details
Multiple integer overflows in the (1) v9fs_xattr_read and (2) v9fs_xattr_write functions in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allow local guest OS administrators to cause a denial of service (QEMU process crash) via a crafted offset, which triggers an out-of-bounds access.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9104
