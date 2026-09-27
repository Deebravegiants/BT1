# [H] ALPINE-CVE-2019-19583

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19583
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19583
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.8.0 <4.12.2-r0
- Alpine:v3.11: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=4.8.0 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=4.8.0 <4.10.4-r2
- Alpine:v3.9: `xen` — affected >=4.8.0 <4.11.3-r1

## Details
An issue was discovered in Xen through 4.12.x allowing x86 HVM/PVH guest OS users to cause a denial of service (guest OS crash) because VMX VMEntry checks mishandle a certain case. Please see XSA-260 for background on the MovSS shadow. Please see XSA-156 for background on the need for #DB interception. The VMX VMEntry checks do not like the exact combination of state which occurs when #DB in intercepted, Single Stepping is active, and blocked by STI/MovSS is active, despite this being a legitimate state to be in. The resulting VMEntry failure is fatal to the guest. HVM/PVH guest userspace code may be able to crash the guest, resulting in a guest Denial of Service. All versions of Xen are affected. Only systems supporting VMX hardware virtual extensions (Intel, Cyrix, or Zhaoxin CPUs) are affected. Arm and AMD systems are unaffected. Only HVM/PVH guests are affected. PV guests cannot leverage the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19583
