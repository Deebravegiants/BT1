# [M] ALPINE-CVE-2018-19876

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19876
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19876
Type: osv

## Affected
- Alpine:v3.10: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.11: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.12: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.13: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.14: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.15: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.16: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.17: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.18: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.19: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.20: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.21: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.22: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.23: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.24: `cairo` — affected >=0 <1.16.0-r1
- Alpine:v3.9: `cairo` — affected >=0 <1.16.0-r1

## Details
cairo 1.16.0, in cairo_ft_apply_variations() in cairo-ft-font.c, would free memory using a free function incompatible with WebKit's fastMalloc, leading to an application crash with a "free(): invalid pointer" error.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19876
