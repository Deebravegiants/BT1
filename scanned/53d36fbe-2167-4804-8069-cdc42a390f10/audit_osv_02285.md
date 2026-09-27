# [H] ALPINE-CVE-2021-40145

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-40145
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40145
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
gdImageGd2Ptr in gd_gd2.c in the GD Graphics Library (aka LibGD) through 2.3.2 has a double free. NOTE: the vendor's position is "The GD2 image format is a proprietary image format of libgd. It has to be regarded as being obsolete, and should only be used for development and testing purposes.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40145
