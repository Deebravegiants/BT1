# [H] BIT-java-2025-32415

## Summary
Severity: High
Advisory: BIT-java-2025-32415
Aliases: BIT-java-min-2025-32415, BIT-jre-2025-32415, CVE-2025-32415
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-32415
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.461

## Details
In libxml2 before 2.13.8 and 2.14.x before 2.14.2, xmlSchemaIDCFillNodeTables in xmlschemas.c has a heap-based buffer under-read. To exploit this, a crafted XML document must be validated against an XML schema with certain identity constraints, or a crafted XML schema must be used.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/890
- https://lists.debian.org/debian-lts-announce/2025/04/msg00041.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-32415
