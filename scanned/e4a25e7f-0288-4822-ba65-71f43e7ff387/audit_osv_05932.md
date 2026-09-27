# [H] BIT-java-2025-24928

## Summary
Severity: High
Advisory: BIT-java-2025-24928
Aliases: BIT-java-min-2025-24928, BIT-jre-2025-24928, CVE-2025-24928
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-24928
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.461

## Details
libxml2 before 2.12.10 and 2.13.x before 2.13.6 has a stack-based buffer overflow in xmlSnprintfElements in valid.c. To exploit this, DTD validation must occur for an untrusted document or untrusted DTD. NOTE: this is similar to CVE-2017-9047.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/847
- https://issues.oss-fuzz.com/issues/392687022
- https://lists.debian.org/debian-lts-announce/2025/02/msg00028.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-24928
- https://security.netapp.com/advisory/ntap-20250321-0006/
