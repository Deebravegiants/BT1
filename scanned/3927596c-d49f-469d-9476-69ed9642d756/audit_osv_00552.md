# [C] ALPINE-CVE-2017-15597

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-15597
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15597
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.11: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.12: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.13: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.14: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.15: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.16: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.17: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.18: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.19: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.20: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.21: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.22: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.23: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.24: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r2
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r3
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r3
- Alpine:v3.7: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.8: `xen` — affected >=0 <4.9.0-r7
- Alpine:v3.9: `xen` — affected >=0 <4.9.0-r7

## Details
An issue was discovered in Xen through 4.9.x. Grant copying code made an implication that any grant pin would be accompanied by a suitable page reference. Other portions of code, however, did not match up with that assumption. When such a grant copy operation is being done on a grant of a dying domain, the assumption turns out wrong. A malicious guest administrator can cause hypervisor memory corruption, most likely resulting in host crash and a Denial of Service. Privilege escalation and information leaks cannot be ruled out.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15597
