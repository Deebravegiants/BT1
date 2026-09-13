# [H] Libxslt: type confusion in xmlnode.psvi between stylesheet and source nodes

## Summary
Severity: High
Advisory: BIT-java-2025-7424
Aliases: BIT-java-min-2025-7424, BIT-jre-2025-7424, CVE-2025-7424
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-7424
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.481

## Details
A flaw was found in the libxslt library. The same memory field, psvi, is used for both stylesheet and input data, which can lead to type confusion during XML transformations. This vulnerability allows an attacker to crash the application or corrupt memory. In some cases, it may lead to denial of service or unexpected behavior.

## References
- http://seclists.org/fulldisclosure/2025/Aug/0
- http://seclists.org/fulldisclosure/2025/Jul/30
- http://seclists.org/fulldisclosure/2025/Jul/32
- http://seclists.org/fulldisclosure/2025/Jul/33
- http://seclists.org/fulldisclosure/2025/Jul/35
- http://seclists.org/fulldisclosure/2025/Jul/37
- http://www.openwall.com/lists/oss-security/2025/07/11/2
- https://access.redhat.com/errata/RHBA-2025:12345
- https://access.redhat.com/errata/RHSA-2026:11015
- https://access.redhat.com/security/cve/CVE-2025-7424
- https://bugzilla.redhat.com/show_bug.cgi?id=2379228
- https://gitlab.gnome.org/GNOME/libxslt/-/issues/139
- https://lists.debian.org/debian-lts-announce/2025/09/msg00024.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-7424
