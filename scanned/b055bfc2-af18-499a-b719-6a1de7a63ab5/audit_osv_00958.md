# [M] ALPINE-CVE-2018-12893

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12893
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12893
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
An issue was discovered in Xen through 4.10.x. One of the fixes in XSA-260 added some safety checks to help prevent Xen livelocking with debug exceptions. Unfortunately, due to an oversight, at least one of these safety checks can be triggered by a guest. A malicious PV guest can crash Xen, leading to a Denial of Service. All Xen systems which have applied the XSA-260 fix are vulnerable. Only x86 systems are vulnerable. ARM systems are not vulnerable. Only x86 PV guests can exploit the vulnerability. x86 HVM and PVH guests cannot exploit the vulnerability. An attacker needs to be able to control hardware debugging facilities to exploit the vulnerability, but such permissions are typically available to unprivileged users.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12893
