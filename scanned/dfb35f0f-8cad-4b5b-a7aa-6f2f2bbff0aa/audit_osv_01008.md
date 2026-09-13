# [M] ALPINE-CVE-2018-15468

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15468
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.0 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15468
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.11: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.12: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.13: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.6: `xen` — affected >=0 <4.8.5-r0
- Alpine:v3.7: `xen` — affected >=0 <4.9.3-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.1-r3
- Alpine:v3.9: `xen` — affected >=0 <4.11.1-r0

## Details
An issue was discovered in Xen through 4.11.x. The DEBUGCTL MSR contains several debugging features, some of which virtualise cleanly, but some do not. In particular, Branch Trace Store is not virtualised by the processor, and software has to be careful to configure it suitably not to lock up the core. As a result, it must only be available to fully trusted guests. Unfortunately, in the case that vPMU is disabled, all value checking was skipped, allowing the guest to choose any MSR_DEBUGCTL setting it likes. A malicious or buggy guest administrator (on Intel x86 HVM or PVH) can lock up the entire host, causing a Denial of Service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15468
