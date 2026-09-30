# [H] ALPINE-CVE-2020-11739

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-11739
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11739
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.2-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r1
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r3
- Alpine:v3.9: `xen` — affected >=0 <4.11.3-r2

## Details
An issue was discovered in Xen through 4.13.x, allowing guest OS users to cause a denial of service or possibly gain privileges because of missing memory barriers in read-write unlock paths. The read-write unlock paths don't contain a memory barrier. On Arm, this means a processor is allowed to re-order the memory access with the preceding ones. In other words, the unlock may be seen by another processor before all the memory accesses within the "critical" section. As a consequence, it may be possible to have a writer executing a critical section at the same time as readers or another writer. In other words, many of the assumptions (e.g., a variable cannot be modified after a check) in the critical sections are not safe anymore. The read-write locks are used in hypercalls (such as grant-table ones), so a malicious guest could exploit the race. For instance, there is a small window where Xen can leak memory if XENMAPSPACE_grant_table is used concurrently. A malicious guest may be able to leak memory, or cause a hypervisor crash resulting in a Denial of Service (DoS). Information leak and privilege escalation cannot be excluded.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11739
