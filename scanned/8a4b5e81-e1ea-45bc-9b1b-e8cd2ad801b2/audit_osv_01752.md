# [M] ALPINE-CVE-2020-14308

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14308
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14308
Type: osv

## Affected
- Alpine:v3.17: `grub` — affected >=0 <2.06-r0
- Alpine:v3.18: `grub` — affected >=0 <2.06-r0
- Alpine:v3.19: `grub` — affected >=0 <2.06-r0
- Alpine:v3.20: `grub` — affected >=0 <2.06-r0
- Alpine:v3.21: `grub` — affected >=0 <2.06-r0
- Alpine:v3.22: `grub` — affected >=0 <2.06-r0
- Alpine:v3.23: `grub` — affected >=0 <2.06-r0
- Alpine:v3.24: `grub` — affected >=0 <2.06-r0

## Details
In grub2 versions before 2.06 the grub memory allocator doesn't check for possible arithmetic overflows on the requested allocation size. This leads the function to return invalid memory allocations which can be further used to cause possible integrity, confidentiality and availability impacts during the boot process.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14308
