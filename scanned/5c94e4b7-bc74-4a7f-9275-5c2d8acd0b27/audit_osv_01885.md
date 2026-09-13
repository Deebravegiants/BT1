# [M] ALPINE-CVE-2020-25602

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25602
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25602
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.11.0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=4.11.0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=4.11.0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=4.11.0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=4.11.0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. An x86 PV guest can trigger a host OS crash when handling guest access to MSR_MISC_ENABLE. When a guest accesses certain Model Specific Registers, Xen first reads the value from hardware to use as the basis for auditing the guest access. For the MISC_ENABLE MSR, which is an Intel specific MSR, this MSR read is performed without error handling for a #GP fault, which is the consequence of trying to read this MSR on non-Intel hardware. A buggy or malicious PV guest administrator can crash Xen, resulting in a host Denial of Service. Only x86 systems are vulnerable. ARM systems are not vulnerable. Only Xen versions 4.11 and onwards are vulnerable. 4.10 and earlier are not vulnerable. Only x86 systems that do not implement the MISC_ENABLE MSR (0x1a0) are vulnerable. AMD and Hygon systems do not implement this MSR and are vulnerable. Intel systems do implement this MSR and are not vulnerable. Other manufacturers have not been checked. Only x86 PV guests can exploit the vulnerability. x86 HVM/PVH guests cannot exploit the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25602
