# [H] ALPINE-CVE-2020-15567

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15567
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15567
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.3-r2
- Alpine:v3.11: `xen` — affected >=0 <4.13.1-r2
- Alpine:v3.12: `xen` — affected >=0 <4.13.1-r2
- Alpine:v3.13: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.14: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.15: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.16: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.17: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.18: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.19: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.20: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.21: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.22: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.23: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.24: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.9: `xen` — affected >=0 <4.11.4-r0

## Details
An issue was discovered in Xen through 4.13.x, allowing Intel guest OS users to gain privileges or cause a denial of service because of non-atomic modification of a live EPT PTE. When mapping guest EPT (nested paging) tables, Xen would in some circumstances use a series of non-atomic bitfield writes. Depending on the compiler version and optimisation flags, Xen might expose a dangerous partially written PTE to the hardware, which an attacker might be able to race to exploit. A guest administrator or perhaps even an unprivileged guest user might be able to cause denial of service, data corruption, or privilege escalation. Only systems using Intel CPUs are vulnerable. Systems using AMD CPUs, and Arm systems, are not vulnerable. Only systems using nested paging (hap, aka nested paging, aka in this case Intel EPT) are vulnerable. Only HVM and PVH guests can exploit the vulnerability. The presence and scope of the vulnerability depends on the precise optimisations performed by the compiler used to build Xen. If the compiler generates (a) a single 64-bit write, or (b) a series of read-modify-write operations in the same order as the source code, the hypervisor is not vulnerable. For example, in one test build using GCC 8.3 with normal settings, the compiler generated multiple (unlocked) read-modify-write operations in source-code order, which did not constitute a vulnerability. We have not been able to survey compilers; consequently we cannot say which compiler(s) might produce vulnerable code (with which code-generation options). The source code clearly violates the C rules, and thus should be considered vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15567
