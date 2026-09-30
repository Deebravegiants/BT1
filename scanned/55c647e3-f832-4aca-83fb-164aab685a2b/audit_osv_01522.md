# [H] ALPINE-CVE-2019-18423

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18423
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18423
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.8 <4.12.1-r1
- Alpine:v3.11: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=4.8 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=4.8 <4.10.4-r1
- Alpine:v3.9: `xen` — affected >=4.8 <4.11.2-r1

## Details
An issue was discovered in Xen through 4.12.x allowing ARM guest OS users to cause a denial of service via a XENMEM_add_to_physmap hypercall. p2m->max_mapped_gfn is used by the functions p2m_resolve_translation_fault() and p2m_get_entry() to sanity check guest physical frame. The rest of the code in the two functions will assume that there is a valid root table and check that with BUG_ON(). The function p2m_get_root_pointer() will ignore the unused top bits of a guest physical frame. This means that the function p2m_set_entry() will alias the frame. However, p2m->max_mapped_gfn will be updated using the original frame. It would be possible to set p2m->max_mapped_gfn high enough to cover a frame that would lead p2m_get_root_pointer() to return NULL in p2m_get_entry() and p2m_resolve_translation_fault(). Additionally, the sanity check on p2m->max_mapped_gfn is off-by-one allowing "highest mapped + 1" to be considered valid. However, p2m_get_root_pointer() will return NULL. The problem could be triggered with a specially crafted hypercall XENMEM_add_to_physmap{, _batch} followed by an access to an address (via hypercall or direct access) that passes the sanity check but cause p2m_get_root_pointer() to return NULL. A malicious guest administrator may cause a hypervisor crash, resulting in a Denial of Service (DoS). Xen version 4.8 and newer are vulnerable. Only Arm systems are vulnerable. x86 systems are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18423
