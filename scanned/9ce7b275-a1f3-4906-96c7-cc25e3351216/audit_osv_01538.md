# [M] ALPINE-CVE-2019-19580

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-19580
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19580
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.2-r0
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
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r2
- Alpine:v3.9: `xen` — affected >=0 <4.11.3-r1

## Details
An issue was discovered in Xen through 4.12.x allowing x86 PV guest OS users to gain host OS privileges by leveraging race conditions in pagetable promotion and demotion operations, because of an incomplete fix for CVE-2019-18421. XSA-299 addressed several critical issues in restartable PV type change operations. Despite extensive testing and auditing, some corner cases were missed. A malicious PV guest administrator may be able to escalate their privilege to that of the host. All security-supported versions of Xen are vulnerable. Only x86 systems are affected. Arm systems are not affected. Only x86 PV guests can leverage the vulnerability. x86 HVM and PVH guests cannot leverage the vulnerability. Note that these attacks require very precise timing, which may be difficult to exploit in practice.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19580
