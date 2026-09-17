# [M] ALPINE-CVE-2023-28484

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-28484
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28484
Type: osv

## Affected
- Alpine:v3.17: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.10.4-r0

## Details
In libxml2 before 2.10.4, parsing of certain invalid XSD schemas can lead to a NULL pointer dereference and subsequently a segfault. This occurs in xmlSchemaFixupComplexType in xmlschemas.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28484
