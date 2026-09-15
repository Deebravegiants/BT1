# [M] ALPINE-CVE-2022-42331

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42331
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42331
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=4.5.0 <4.15.5-r0
- Alpine:v3.16: `xen` — affected >=4.5.0 <4.16.4-r0
- Alpine:v3.17: `xen` — affected >=4.5.0 <4.16.4-r0
- Alpine:v3.18: `xen` — affected >=4.5.0 <4.17.0-r5
- Alpine:v3.19: `xen` — affected >=4.5.0 <4.17.0-r5
- Alpine:v3.20: `xen` — affected >=4.5.0 <4.17.0-r5
- Alpine:v3.21: `xen` — affected >=4.5.0 <4.17.0-r5
- Alpine:v3.22: `xen` — affected >=4.5.0 <4.17.0-r5
- Alpine:v3.23: `xen` — affected >=4.5.0 <4.17.0-r5
- Alpine:v3.24: `xen` — affected >=4.5.0 <4.17.0-r5

## Details
x86: speculative vulnerability in 32bit SYSCALL path Due to an oversight in the very original Spectre/Meltdown security work (XSA-254), one entrypath performs its speculation-safety actions too late. In some configurations, there is an unprotected RET instruction which can be attacked with a variety of speculative attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42331
