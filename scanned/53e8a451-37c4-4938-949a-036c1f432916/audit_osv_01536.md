# [H] ALPINE-CVE-2019-19578

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19578
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19578
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
An issue was discovered in Xen through 4.12.x allowing x86 PV guest OS users to cause a denial of service via degenerate chains of linear pagetables, because of an incorrect fix for CVE-2017-15595. "Linear pagetables" is a technique which involves either pointing a pagetable at itself, or to another pagetable of the same or higher level. Xen has limited support for linear pagetables: A page may either point to itself, or point to another pagetable of the same level (i.e., L2 to L2, L3 to L3, and so on). XSA-240 introduced an additional restriction that limited the "depth" of such chains by allowing pages to either *point to* other pages of the same level, or *be pointed to* by other pages of the same level, but not both. To implement this, we keep track of the number of outstanding times a page points to or is pointed to another page table, to prevent both from happening at the same time. Unfortunately, the original commit introducing this reset this count when resuming validation of a partially-validated pagetable, incorrectly dropping some "linear_pt_entry" counts. If an attacker could engineer such a situation to occur, they might be able to make loops or other arbitrary chains of linear pagetables, as described in XSA-240. A malicious or buggy PV guest may cause the hypervisor to crash, resulting in Denial of Service (DoS) affecting the entire host. Privilege escalation and information leaks cannot be excluded. All versions of Xen are vulnerable. Only x86 systems are affected. Arm systems are not affected. Only x86 PV guests can leverage the vulnerability. x86 HVM and PVH guests cannot leverage the vulnerability. Only systems which have enabled linear pagetables are vulnerable. Systems which have disabled linear pagetables, either by selecting CONFIG_PV_LINEAR_PT=n when building the hypervisor, or adding pv-linear-pt=false on the command-line, are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19578
