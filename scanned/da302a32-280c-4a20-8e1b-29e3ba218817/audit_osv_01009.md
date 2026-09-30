# [M] ALPINE-CVE-2018-15469

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15469
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15469
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
An issue was discovered in Xen through 4.11.x. ARM never properly implemented grant table v2, either in the hypervisor or in Linux. Unfortunately, an ARM guest can still request v2 grant tables; they will simply not be properly set up, resulting in subsequent grant-related hypercalls hitting BUG() checks. An unprivileged guest can cause a BUG() check in the hypervisor, resulting in a denial-of-service (crash).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15469
