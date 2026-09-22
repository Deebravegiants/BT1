# [M] ALPINE-CVE-2019-11038

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-11038
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11038
Type: osv

## Affected
- Alpine:v3.10: `gd` — affected >=0 <2.2.5-r3
- Alpine:v3.11: `gd` — affected >=0 <2.2.5-r3
- Alpine:v3.12: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.13: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.14: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.15: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.16: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.17: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.18: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.19: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.20: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.21: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.22: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.23: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.24: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.8: `gd` — affected >=0 <2.2.5-r3
- Alpine:v3.9: `gd` — affected >=0 <2.2.5-r3

## Details
When using the gdImageCreateFromXbm() function in the GD Graphics Library (aka LibGD) 2.2.5, as used in the PHP GD extension in PHP versions 7.1.x below 7.1.30, 7.2.x below 7.2.19 and 7.3.x below 7.3.6, it is possible to supply data that will cause the function to use the value of uninitialized variable. This may lead to disclosing contents of the stack that has been left there by previous code.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11038
