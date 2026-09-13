# [M] ALPINE-CVE-2016-7777

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-7777
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.3 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2016-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7777
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.11: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.12: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.13: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.14: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.15: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.16: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.17: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.18: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.19: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.20: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.21: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.22: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.23: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.24: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r3
- Alpine:v3.5: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.6: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.7: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.8: `xen` — affected >=0 <4.7.0-r5
- Alpine:v3.9: `xen` — affected >=0 <4.7.0-r5

## Details
Xen 4.7.x and earlier does not properly honor CR0.TS and CR0.EM, which allows local x86 HVM guest OS users to read or modify FPU, MMX, or XMM register state information belonging to arbitrary tasks on the guest by modifying an instruction while the hypervisor is preparing to emulate it.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7777
