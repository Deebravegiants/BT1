# [M] ALPINE-CVE-2019-19582

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-19582
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19582
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
An issue was discovered in Xen through 4.12.x allowing x86 guest OS users to cause a denial of service (infinite loop) because certain bit iteration is mishandled. In a number of places bitmaps are being used by the hypervisor to track certain state. Iteration over all bits involves functions which may misbehave in certain corner cases: On x86 accesses to bitmaps with a compile time known size of 64 may incur undefined behavior, which may in particular result in infinite loops. A malicious guest may cause a hypervisor crash or hang, resulting in a Denial of Service (DoS). All versions of Xen are vulnerable. x86 systems with 64 or more nodes are vulnerable (there might not be any such systems that Xen would run on). x86 systems with less than 64 nodes are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19582
