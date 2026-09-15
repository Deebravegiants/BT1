# [H] ALPINE-CVE-2023-34322

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-34322
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34322
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.15.5-r1
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.16.5-r1
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.16.5-r1
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.17.2-r1
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.17.2-r1
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.17.2-r1
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.17.2-r1
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.17.2-r1
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.17.2-r1
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.17.2-r1

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
- https://security.alpinelinux.org/vuln/CVE-2023-34322
