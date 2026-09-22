# [H] ALPINE-CVE-2024-28757

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-28757
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-28757
Type: osv

## Affected
- Alpine:v3.16: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.17: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.18: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.19: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.20: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.21: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.22: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.23: `expat` — affected >=0 <2.6.2-r0
- Alpine:v3.24: `expat` — affected >=0 <2.6.2-r0

## Details
libexpat through 2.6.1 allows an XML Entity Expansion attack when there is isolated use of external parsers (created via XML_ExternalEntityParserCreate).

## References
- https://security.alpinelinux.org/vuln/CVE-2024-28757
