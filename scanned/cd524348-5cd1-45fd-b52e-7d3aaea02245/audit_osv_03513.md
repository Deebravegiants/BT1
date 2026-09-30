# [H] ALPINE-CVE-2026-23558

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-23558
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-23558
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.18.5-r7
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.19.5-r2
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.20.3-r2
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.20.3-r2
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.21.1-r3

## Details
The adjustments made for XSA-379 as well as those subsequently becoming
XSA-387 still left a race window, when a HVM or PVH guest does a grant
table version change from v2 to v1 in parallel with mapping the status
page(s) via XENMEM_add_to_physmap.  Some of the status pages may then be
freed while mappings of them would still be inserted into the guest's
secondary (P2M) page tables.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-23558
