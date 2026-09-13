# [H] ALPINE-CVE-2022-43680

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-43680
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-43680
Type: osv

## Affected
- Alpine:v3.13: `expat` — affected >=0 <2.2.10-r8
- Alpine:v3.14: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.15: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.16: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.17: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.18: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.19: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.20: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.21: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.22: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.23: `expat` — affected >=0 <2.5.0-r0
- Alpine:v3.24: `expat` — affected >=0 <2.5.0-r0

## Details
In libexpat through 2.4.9, there is a use-after free caused by overeager destruction of a shared DTD in XML_ExternalEntityParserCreate in out-of-memory situations.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-43680
