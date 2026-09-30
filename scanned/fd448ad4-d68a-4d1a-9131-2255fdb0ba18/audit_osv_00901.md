# [H] ALPINE-CVE-2018-10873

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10873
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10873
Type: osv

## Affected
- Alpine:v3.10: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.11: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.12: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.13: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.14: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.15: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.16: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.17: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.18: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.19: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.20: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.21: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.22: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.23: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.24: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.5: `spice` — affected >=0 <0.12.8-r4
- Alpine:v3.6: `spice` — affected >=0 <0.13.3-r3
- Alpine:v3.7: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.8: `spice` — affected >=0 <0.14.1-r0
- Alpine:v3.9: `spice` — affected >=0 <0.14.1-r0

## Details
A vulnerability was discovered in SPICE before version 0.14.1 where the generated code used for demarshalling messages lacked sufficient bounds checks. A malicious client or server, after authentication, could send specially crafted messages to its peer which would result in a crash or, potentially, other impacts.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10873
