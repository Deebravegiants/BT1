# [H] ALPINE-CVE-2026-42487

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42487
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42487
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=0 <4.18.5-r9
- Alpine:v3.21: `xen` — affected >=0 <4.19.5-r4
- Alpine:v3.22: `xen` — affected >=0 <4.20.3-r4
- Alpine:v3.23: `xen` — affected >=0 <4.20.3-r4
- Alpine:v3.24: `xen` — affected >=0 <4.21.1-r6

## Details
HVM guest I/O port accesses are subject to either emulation or at least
translation.  Translations are managed by the device model (via
XEN_DOMCTL_ioport_mapping), and hence the linked list used may changed
at any time.  Traversal of those lists (while handling guest I/O port
accesses) therefore needs synchronizing with updates, which was missing
so far.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42487
