# [M] ALPINE-CVE-2022-27672

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-27672
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27672
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=0 <4.16.4-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.4-r0
- Alpine:v3.18: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.19: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.20: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.21: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.22: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.23: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.24: `xen` — affected >=0 <4.17.0-r2

## Details
When SMT is enabled, certain AMD processors may speculatively execute instructions using a target
from the sibling thread after an SMT mode switch potentially resulting in information disclosure.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27672
