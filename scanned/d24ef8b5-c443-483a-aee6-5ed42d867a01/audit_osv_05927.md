# [C] BIT-java-2024-56171

## Summary
Severity: Critical
Advisory: BIT-java-2024-56171
Aliases: BIT-java-min-2024-56171, BIT-jre-2024-56171, CVE-2024-56171
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-56171
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.461

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
- https://nvd.nist.gov/vuln/detail/CVE-2024-56171
- https://security.netapp.com/advisory/ntap-20250328-0010/
