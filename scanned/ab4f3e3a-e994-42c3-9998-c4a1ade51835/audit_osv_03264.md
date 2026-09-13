# [H] ALPINE-CVE-2025-32415

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-32415
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-32415
Type: osv

## Affected
- Alpine:v3.18: `libxml2` — affected >=2.14.0 <2.11.8-r3
- Alpine:v3.19: `libxml2` — affected >=2.14.0 <2.11.8-r3
- Alpine:v3.20: `libxml2` — affected >=2.14.0 <2.12.10-r0
- Alpine:v3.21: `libxml2` — affected >=2.14.0 <2.13.4-r6
- Alpine:v3.22: `libxml2` — affected >=2.14.0 <2.13.8-r0
- Alpine:v3.23: `libxml2` — affected >=2.14.0 <2.13.8-r0
- Alpine:v3.24: `libxml2` — affected >=2.14.0 <2.13.8-r0

## Details
In libxml2 before 2.13.8 and 2.14.x before 2.14.2, xmlSchemaIDCFillNodeTables in xmlschemas.c has a heap-based buffer under-read. To exploit this, a crafted XML document must be validated against an XML schema with certain identity constraints, or a crafted XML schema must be used.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-32415
