# [C] ALPINE-CVE-2017-2620

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-2620
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2620
Type: osv

## Affected
- Alpine:v3.10: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0
- Alpine:v3.6: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.7: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.8: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.9: `qemu` — affected >=0 <2.8.1-r1
- Alpine:v3.10: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.11: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.12: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.13: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.14: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.15: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.16: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.17: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.18: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.19: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.20: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.21: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.22: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.23: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.24: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.3: `xen` — affected >=0 <4.6.3-r8
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r10
- Alpine:v3.5: `xen` — affected >=0 <4.7.1-r5
- Alpine:v3.6: `xen` — affected >=0 <4.7.1-r5

## Details
Quick emulator (QEMU) before 2.8 built with the Cirrus CLGD 54xx VGA Emulator support is vulnerable to an out-of-bounds access issue. The issue could occur while copying VGA data in cirrus_bitblt_cputovideo. A privileged user inside guest could use this flaw to crash the QEMU process OR potentially execute arbitrary code on host with privileges of the QEMU process.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2620
