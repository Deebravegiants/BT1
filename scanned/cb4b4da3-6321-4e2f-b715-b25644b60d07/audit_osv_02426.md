# [M] ALPINE-CVE-2022-23034

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-23034
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23034
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=3.2.0 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=3.2.0 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=3.2.0 <4.15.2-r0
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.15.2-r0
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.16.1-r0
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.16.1-r0

## Details
A PV guest could DoS Xen while unmapping a grant To address XSA-380, reference counting was introduced for grant mappings for the case where a PV guest would have the IOMMU enabled. PV guests can request two forms of mappings. When both are in use for any individual mapping, unmapping of such a mapping can be requested in two steps. The reference count for such a mapping would then mistakenly be decremented twice. Underflow of the counters gets detected, resulting in the triggering of a hypervisor bug check.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23034
