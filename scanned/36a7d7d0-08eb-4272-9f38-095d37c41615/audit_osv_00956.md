# [M] ALPINE-CVE-2018-12891

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12891
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12891
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.11: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.11.0-r0
- Alpine:v3.5: `xen` — affected >=0 <4.7.6-r0
- Alpine:v3.6: `xen` — affected >=0 <4.8.4-r0
- Alpine:v3.7: `xen` — affected >=0 <4.9.3-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.1-r3
- Alpine:v3.9: `xen` — affected >=0 <4.11.0-r0

## Details
An issue was discovered in Xen through 4.10.x. Certain PV MMU operations may take a long time to process. For that reason Xen explicitly checks for the need to preempt the current vCPU at certain points. A few rarely taken code paths did bypass such checks. By suitably enforcing the conditions through its own page table contents, a malicious guest may cause such bypasses to be used for an unbounded number of iterations. A malicious or buggy PV guest may cause a Denial of Service (DoS) affecting the entire host. Specifically, it may prevent use of a physical CPU for an indeterminate period of time. All Xen versions from 3.4 onwards are vulnerable. Xen versions 3.3 and earlier are vulnerable to an even wider class of attacks, due to them lacking preemption checks altogether in the affected code paths. Only x86 systems are affected. ARM systems are not affected. Only multi-vCPU x86 PV guests can leverage the vulnerability. x86 HVM or PVH guests as well as x86 single-vCPU PV ones cannot leverage the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12891
