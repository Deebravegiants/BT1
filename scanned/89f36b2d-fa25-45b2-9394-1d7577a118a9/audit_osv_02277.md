# [M] ALPINE-CVE-2021-38115

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-38115
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-38115
Type: osv

## Affected
- Alpine:v3.11: `gd` — affected >=0 <2.2.5-r4
- Alpine:v3.12: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.13: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.14: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.15: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.16: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.17: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.18: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.19: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.20: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.21: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.22: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.23: `gd` — affected >=0 <2.3.0-r1
- Alpine:v3.24: `gd` — affected >=0 <2.3.0-r1

## Details
read_header_tga in gd_tga.c in the GD Graphics Library (aka LibGD) through 2.3.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-38115
