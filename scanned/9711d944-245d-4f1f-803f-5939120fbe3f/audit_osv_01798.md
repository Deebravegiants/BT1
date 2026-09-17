# [M] ALPINE-CVE-2020-15563

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15563
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15563
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.8.0 <4.12.3-r2
- Alpine:v3.11: `xen` — affected >=4.8.0 <4.13.1-r2
- Alpine:v3.12: `xen` — affected >=4.8.0 <4.13.1-r2
- Alpine:v3.13: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.14: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.15: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.16: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.17: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.18: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.19: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.20: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.21: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.22: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.23: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.24: `xen` — affected >=4.8.0 <4.13.1-r4
- Alpine:v3.9: `xen` — affected >=4.8.0 <4.11.4-r0

## Details
An issue was discovered in Xen through 4.13.x, allowing x86 HVM guest OS users to cause a hypervisor crash. An inverted conditional in x86 HVM guests' dirty video RAM tracking code allows such guests to make Xen de-reference a pointer guaranteed to point at unmapped space. A malicious or buggy HVM guest may cause the hypervisor to crash, resulting in Denial of Service (DoS) affecting the entire host. Xen versions from 4.8 onwards are affected. Xen versions 4.7 and earlier are not affected. Only x86 systems are affected. Arm systems are not affected. Only x86 HVM guests using shadow paging can leverage the vulnerability. In addition, there needs to be an entity actively monitoring a guest's video frame buffer (typically for display purposes) in order for such a guest to be able to leverage the vulnerability. x86 PV guests, as well as x86 HVM guests using hardware assisted paging (HAP), cannot leverage the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15563
