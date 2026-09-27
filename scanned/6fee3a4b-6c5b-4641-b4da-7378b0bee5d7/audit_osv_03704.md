# [H] ALPINE-CVE-2026-42493

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42493
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42493
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
Addressing certain issues, in particular related to operations which may
take excessively long and therefore would need preemption, has turned out
overly costly.  Since alternatives (HVM/PVH: HAP, PV: shim) are commonly
available, the decision was to deprecate the functionality, while still
retaining it for people to use at their own (security) risk.  Memory-wise
small enough guests may still be okay to run.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42493
