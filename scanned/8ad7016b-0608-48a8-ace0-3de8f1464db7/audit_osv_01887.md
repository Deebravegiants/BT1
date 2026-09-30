# [M] ALPINE-CVE-2020-25604

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25604
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25604
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
An issue was discovered in Xen through 4.14.x. There is a race condition when migrating timers between x86 HVM vCPUs. When migrating timers of x86 HVM guests between its vCPUs, the locking model used allows for a second vCPU of the same guest (also operating on the timers) to release a lock that it didn't acquire. The most likely effect of the issue is a hang or crash of the hypervisor, i.e., a Denial of Service (DoS). All versions of Xen are affected. Only x86 systems are vulnerable. Arm systems are not vulnerable. Only x86 HVM guests can leverage the vulnerability. x86 PV and PVH cannot leverage the vulnerability. Only guests with more than one vCPU can exploit the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25604
