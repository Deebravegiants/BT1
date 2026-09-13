# [M] ALPINE-CVE-2020-15564

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15564
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15564
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
An issue was discovered in Xen through 4.13.x, allowing Arm guest OS users to cause a hypervisor crash because of a missing alignment check in VCPUOP_register_vcpu_info. The hypercall VCPUOP_register_vcpu_info is used by a guest to register a shared region with the hypervisor. The region will be mapped into Xen address space so it can be directly accessed. On Arm, the region is accessed with instructions that require a specific alignment. Unfortunately, there is no check that the address provided by the guest will be correctly aligned. As a result, a malicious guest could cause a hypervisor crash by passing a misaligned address. A malicious guest administrator may cause a hypervisor crash, resulting in a Denial of Service (DoS). All Xen versions are vulnerable. Only Arm systems are vulnerable. x86 systems are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15564
