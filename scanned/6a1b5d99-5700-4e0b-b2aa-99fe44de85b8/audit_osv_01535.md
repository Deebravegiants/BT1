# [H] ALPINE-CVE-2019-19577

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19577
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.2 (CVSS:3.1/AV:P/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19577
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
An issue was discovered in Xen through 4.12.x allowing x86 AMD HVM guest OS users to cause a denial of service or possibly gain privileges by triggering data-structure access during pagetable-height updates. When running on AMD systems with an IOMMU, Xen attempted to dynamically adapt the number of levels of pagetables (the pagetable height) in the IOMMU according to the guest's address space size. The code to select and update the height had several bugs. Notably, the update was done without taking a lock which is necessary for safe operation. A malicious guest administrator can cause Xen to access data structures while they are being modified, causing Xen to crash. Privilege escalation is thought to be very difficult but cannot be ruled out. Additionally, there is a potential memory leak of 4kb per guest boot, under memory pressure. Only Xen on AMD CPUs is vulnerable. Xen running on Intel CPUs is not vulnerable. ARM systems are not vulnerable. Only systems where guests are given direct access to physical devices are vulnerable. Systems which do not use PCI pass-through are not vulnerable. Only HVM guests can exploit the vulnerability. PV and PVH guests cannot. All versions of Xen with IOMMU support are vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19577
