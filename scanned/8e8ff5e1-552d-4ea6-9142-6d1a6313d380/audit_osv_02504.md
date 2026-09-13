# [H] ALPINE-CVE-2022-27406

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27406
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27406
Type: osv

## Affected
- Alpine:v3.12: `freetype` — affected >=0 <2.10.4-r2
- Alpine:v3.13: `freetype` — affected >=0 <2.10.4-r3
- Alpine:v3.14: `freetype` — affected >=0 <2.10.4-r3
- Alpine:v3.15: `freetype` — affected >=0 <2.11.1-r2
- Alpine:v3.16: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.17: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.18: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.19: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.20: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.21: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.22: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.23: `freetype` — affected >=0 <2.12.1-r0
- Alpine:v3.24: `freetype` — affected >=0 <2.12.1-r0

## Details
FreeType commit 22a0cccb4d9d002f33c1ba7a4b36812c7d4f46b5 was discovered to contain a segmentation violation via the function FT_Request_Size.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27406
