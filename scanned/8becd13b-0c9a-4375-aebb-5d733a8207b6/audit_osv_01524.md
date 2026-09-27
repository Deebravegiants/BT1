# [C] ALPINE-CVE-2019-18425

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-18425
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18425
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.1-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r1

## Details
An issue was discovered in Xen through 4.12.x allowing 32-bit PV guest OS users to gain guest OS privileges by installing and using descriptors. There is missing descriptor table limit checking in x86 PV emulation. When emulating certain PV guest operations, descriptor table accesses are performed by the emulating code. Such accesses should respect the guest specified limits, unless otherwise guaranteed to fail in such a case. Without this, emulation of 32-bit guest user mode calls through call gates would allow guest user mode to install and then use descriptors of their choice, as long as the guest kernel did not itself install an LDT. (Most OSes don't install any LDT by default). 32-bit PV guest user mode can elevate its privileges to that of the guest kernel. Xen versions from at least 3.2 onwards are affected. Only 32-bit PV guest user mode can leverage this vulnerability. HVM, PVH, as well as 64-bit PV guests cannot leverage this vulnerability. Arm systems are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18425
