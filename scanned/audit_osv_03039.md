# [H] ALPINE-CVE-2024-31142

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-31142
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-31142
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=4.16.0 <4.16.6-r0
- Alpine:v3.17: `xen` — affected >=4.16.0 <4.16.6-r0
- Alpine:v3.18: `xen` — affected >=4.16.0 <4.17.4-r0
- Alpine:v3.19: `xen` — affected >=4.16.0 <4.18.2-r0
- Alpine:v3.20: `xen` — affected >=4.16.0 <4.18.2-r0
- Alpine:v3.21: `xen` — affected >=4.16.0 <4.18.2-r0
- Alpine:v3.22: `xen` — affected >=4.16.0 <4.18.2-r0
- Alpine:v3.23: `xen` — affected >=4.16.0 <4.18.2-r0
- Alpine:v3.24: `xen` — affected >=4.16.0 <4.18.2-r0

## Details
Because of a logical error in XSA-407 (Branch Type Confusion), the
mitigation is not applied properly when it is intended to be used.
XSA-434 (Speculative Return Stack Overflow) uses the same
infrastructure, so is equally impacted.

For more details, see:
  https://xenbits.xen.org/xsa/advisory-407.html
  https://xenbits.xen.org/xsa/advisory-434.html

## References
- https://security.alpinelinux.org/vuln/CVE-2024-31142
