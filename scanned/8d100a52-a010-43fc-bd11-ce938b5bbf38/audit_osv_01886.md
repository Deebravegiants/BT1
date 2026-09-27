# [H] ALPINE-CVE-2020-25603

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25603
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25603
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. There are missing memory barriers when accessing/allocating an event channel. Event channels control structures can be accessed lockless as long as the port is considered to be valid. Such a sequence is missing an appropriate memory barrier (e.g., smp_*mb()) to prevent both the compiler and CPU from re-ordering access. A malicious guest may be able to cause a hypervisor crash resulting in a Denial of Service (DoS). Information leak and privilege escalation cannot be excluded. Systems running all versions of Xen are affected. Whether a system is vulnerable will depend on the CPU and compiler used to build Xen. For all systems, the presence and the scope of the vulnerability depend on the precise re-ordering performed by the compiler used to build Xen. We have not been able to survey compilers; consequently we cannot say which compiler(s) might produce vulnerable code (with which code generation options). GCC documentation clearly suggests that re-ordering is possible. Arm systems will also be vulnerable if the CPU is able to re-order memory access. Please consult your CPU vendor. x86 systems are only vulnerable if a compiler performs re-ordering.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25603
