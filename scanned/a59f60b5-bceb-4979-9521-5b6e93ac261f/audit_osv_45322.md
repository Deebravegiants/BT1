# [C] libxml2 before 2.12.10 and 2.13.x before 2.13.6 has a use-after-free in xmlSchemaIDCFillNodeTables...

## Summary
Severity: Critical
Advisory: JLSEC-2025-86
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-86
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.13.6+1

## Details
libxml2 before 2.12.10 and 2.13.x before 2.13.6 has a use-after-free in xmlSchemaIDCFillNodeTables and xmlSchemaBubbleIDCNodeTables in xmlschemas.c. To exploit this, a crafted XML document must be validated against an XML schema with certain identity constraints, or a crafted XML schema must be used.

## References
- http://seclists.org/fulldisclosure/2025/Apr/10
- http://seclists.org/fulldisclosure/2025/Apr/11
- http://seclists.org/fulldisclosure/2025/Apr/12
- http://seclists.org/fulldisclosure/2025/Apr/13
- http://seclists.org/fulldisclosure/2025/Apr/4
- http://seclists.org/fulldisclosure/2025/Apr/5
- http://seclists.org/fulldisclosure/2025/Apr/8
- http://seclists.org/fulldisclosure/2025/Apr/9
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/828
- https://lists.debian.org/debian-lts-announce/2025/02/msg00028.html
- https://security.netapp.com/advisory/ntap-20250328-0010/
