# [H] ALPINE-CVE-2021-28707

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28707
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28707
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.7.0 <4.13.4-r2
- Alpine:v3.12: `xen` — affected >=4.7.0 <4.13.4-r2
- Alpine:v3.13: `xen` — affected >=4.7.0 <4.14.3-r2
- Alpine:v3.14: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.15: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.16: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.17: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.18: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.19: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.20: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.21: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.22: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.23: `xen` — affected >=4.7.0 <4.15.1-r2
- Alpine:v3.24: `xen` — affected >=4.7.0 <4.15.1-r2

## Details
PoD operations on misaligned GFNs T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] x86 HVM and PVH guests may be started in populate-on-demand (PoD) mode, to provide a way for them to later easily have more memory assigned. Guests are permitted to control certain P2M aspects of individual pages via hypercalls. These hypercalls may act on ranges of pages specified via page orders (resulting in a power-of-2 number of pages). The implementation of some of these hypercalls for PoD does not enforce the base page frame number to be suitably aligned for the specified order, yet some code involved in PoD handling actually makes such an assumption. These operations are XENMEM_decrease_reservation (CVE-2021-28704) and XENMEM_populate_physmap (CVE-2021-28707), the latter usable only by domains controlling the guest, i.e. a de-privileged qemu or a stub domain. (Patch 1, combining the fix to both these two issues.) In addition handling of XENMEM_decrease_reservation can also trigger a host crash when the specified page order is neither 4k nor 2M nor 1G (CVE-2021-28708, patch 2).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28707
