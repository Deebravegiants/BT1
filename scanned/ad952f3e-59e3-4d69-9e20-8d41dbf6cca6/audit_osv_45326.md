# [H] In libxml2 before 2.13.8 and 2.14.x before 2.14.2, xmlSchemaIDCFillNodeTables in xmlschemas.c has a...

## Summary
Severity: High
Advisory: JLSEC-2025-90
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-90
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.14.1+0 <2.14.4+0

## Details
In libxml2 before 2.13.8 and 2.14.x before 2.14.2, xmlSchemaIDCFillNodeTables in xmlschemas.c has a heap-based buffer under-read. To exploit this, a crafted XML document must be validated against an XML schema with certain identity constraints, or a crafted XML schema must be used.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/890
- https://lists.debian.org/debian-lts-announce/2025/04/msg00041.html
