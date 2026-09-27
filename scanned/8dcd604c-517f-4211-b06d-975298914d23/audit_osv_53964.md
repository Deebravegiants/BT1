# [H] CVE-2023-34322

## Summary
Severity: High
Advisory: CVE-2023-34322
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-34322
Type: osv

## Details
For migration as well as to work around kernels unaware of L1TF (see
XSA-273), PV guests may be run in shadow paging mode.  Since Xen itself
needs to be mapped when PV guests run, Xen and shadowed PV guests run
directly the respective shadow page tables.  For 64-bit PV guests this
means running on the shadow of the guest root page table.

In the course of dealing with shortage of memory in the shadow pool
associated with a domain, shadows of page tables may be torn down.  This
tearing down may include the shadow root page table that the CPU in
question is presently running on.  While a precaution exists to
supposedly prevent the tearing down of the underlying live page table,
the time window covered by that precaution isn't large enough.

## References
- https://xenbits.xenproject.org/xsa/advisory-438.html
- http://xenbits.xen.org/xsa/advisory-438.html
