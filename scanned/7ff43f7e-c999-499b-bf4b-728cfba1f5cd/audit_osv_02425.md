# [H] ALPINE-CVE-2022-23033

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-23033
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23033
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=4.12.0 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=4.12.0 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=4.12.0 <4.15.2-r0
- Alpine:v3.15: `xen` — affected >=4.12.0 <4.15.2-r0
- Alpine:v3.16: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.17: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.18: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.19: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.20: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.21: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.22: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.23: `xen` — affected >=4.12.0 <4.16.1-r0
- Alpine:v3.24: `xen` — affected >=4.12.0 <4.16.1-r0

## Details
arm: guest_physmap_remove_page not removing the p2m mappings The functions to remove one or more entries from a guest p2m pagetable on Arm (p2m_remove_mapping, guest_physmap_remove_page, and p2m_set_entry with mfn set to INVALID_MFN) do not actually clear the pagetable entry if the entry doesn't have the valid bit set. It is possible to have a valid pagetable entry without the valid bit set when a guest operating system uses set/way cache maintenance instructions. For instance, a guest issuing a set/way cache maintenance instruction, then calling the XENMEM_decrease_reservation hypercall to give back memory pages to Xen, might be able to retain access to those pages even after Xen started reusing them for other purposes.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23033
