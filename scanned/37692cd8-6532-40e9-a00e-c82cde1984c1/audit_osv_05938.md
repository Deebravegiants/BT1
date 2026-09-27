# [H] BIT-java-2025-32414

## Summary
Severity: High
Advisory: BIT-java-2025-32414
Aliases: BIT-java-min-2025-32414, BIT-jre-2025-32414, CVE-2025-32414
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-32414
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.461

## Details
In libxml2 before 2.13.8 and 2.14.x before 2.14.2, out-of-bounds memory access can occur in the Python API (Python bindings) because of an incorrect return value. This occurs in xmlPythonFileRead and xmlPythonFileReadRaw because of a difference between bytes and characters.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/889
- https://lists.debian.org/debian-lts-announce/2025/04/msg00041.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-32414
