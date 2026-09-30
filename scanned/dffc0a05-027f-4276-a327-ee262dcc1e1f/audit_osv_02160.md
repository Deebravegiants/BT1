# [M] ALPINE-CVE-2021-28693

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28693
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28693
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.12.0 <4.13.3-r1
- Alpine:v3.12: `xen` — affected >=4.12.0 <4.13.3-r1
- Alpine:v3.13: `xen` — affected >=4.12.0 <4.14.1-r3
- Alpine:v3.14: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.15: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.16: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.17: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.18: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.19: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.20: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.21: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.22: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.23: `xen` — affected >=4.12.0 <4.15.0-r1
- Alpine:v3.24: `xen` — affected >=4.12.0 <4.15.0-r1

## Details
xen/arm: Boot modules are not scrubbed The bootloader will load boot modules (e.g. kernel, initramfs...) in a temporary area before they are copied by Xen to each domain memory. To ensure sensitive data is not leaked from the modules, Xen must "scrub" them before handing the page over to the allocator. Unfortunately, it was discovered that modules will not be scrubbed on Arm.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28693
