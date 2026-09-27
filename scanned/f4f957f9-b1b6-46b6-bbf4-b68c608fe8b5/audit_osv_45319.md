# [M] In libxml2 before 2.10.4, parsing of certain invalid XSD schemas can lead to a NULL pointer...

## Summary
Severity: Medium
Advisory: JLSEC-2025-79
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-79
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.11.5+0 <2.12.0+0

## Details
In libxml2 before 2.10.4, parsing of certain invalid XSD schemas can lead to a NULL pointer dereference and subsequently a segfault. This occurs in xmlSchemaFixupComplexType in xmlschemas.c.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/491
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.10.4
- https://lists.debian.org/debian-lts-announce/2023/04/msg00031.html
- https://security.netapp.com/advisory/ntap-20230601-0006/
- https://security.netapp.com/advisory/ntap-20240201-0005/
