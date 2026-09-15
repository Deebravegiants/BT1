# [M] ALPINE-CVE-2020-25598

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25598
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25598
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.12.0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=4.12.0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=4.12.0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=4.12.0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=4.12.0 <4.14.0-r1

## Details
An issue was discovered in Xen 4.14.x. There is a missing unlock in the XENMEM_acquire_resource error path. The RCU (Read, Copy, Update) mechanism is a synchronisation primitive. A buggy error path in the XENMEM_acquire_resource exits without releasing an RCU reference, which is conceptually similar to forgetting to unlock a spinlock. A buggy or malicious HVM stubdomain can cause an RCU reference to be leaked. This causes subsequent administration operations, (e.g., CPU offline) to livelock, resulting in a host Denial of Service. The buggy codepath has been present since Xen 4.12. Xen 4.14 and later are vulnerable to the DoS. The side effects are believed to be benign on Xen 4.12 and 4.13, but patches are provided nevertheless. The vulnerability can generally only be exploited by x86 HVM VMs, as these are generally the only type of VM that have a Qemu stubdomain. x86 PV and PVH domains, as well as ARM VMs, typically don't use a stubdomain. Only VMs using HVM stubdomains can exploit the vulnerability. VMs using PV stubdomains, or with emulators running in dom0, cannot exploit the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25598
