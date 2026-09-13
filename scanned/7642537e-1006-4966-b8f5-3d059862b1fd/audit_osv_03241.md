# [C] ALPINE-CVE-2025-27466

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-27466
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27466
Type: osv

## Affected
- Alpine:v3.19: `xen` — affected >=4.13.0 <4.18.5-r2
- Alpine:v3.20: `xen` — affected >=4.13.0 <4.18.5-r2
- Alpine:v3.21: `xen` — affected >=4.13.0 <4.19.3-r1
- Alpine:v3.22: `xen` — affected >=4.13.0 <4.20.1-r1
- Alpine:v3.23: `xen` — affected >=4.13.0 <4.20.1-r1
- Alpine:v3.24: `xen` — affected >=4.13.0 <4.20.1-r1

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

There are multiple issues related to the handling and accessing of guest
memory pages in the viridian code:

 1. A NULL pointer dereference in the updating of the reference TSC area.
    This is CVE-2025-27466.

 2. A NULL pointer dereference by assuming the SIM page is mapped when
    a synthetic timer message has to be delivered.  This is
    CVE-2025-58142.

 3. A race in the mapping of the reference TSC page, where a guest can
    get Xen to free a page while still present in the guest physical to
    machine (p2m) page tables.  This is CVE-2025-58143.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27466
