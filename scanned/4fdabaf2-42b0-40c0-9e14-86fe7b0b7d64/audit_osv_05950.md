# [H] Libxslt: libxml2: heap use-after-free in libxslt caused by atype corruption in xmlattrptr

## Summary
Severity: High
Advisory: BIT-java-2025-7425
Aliases: BIT-java-min-2025-7425, BIT-jre-2025-7425, CVE-2025-7425
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-7425
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.481

## Details
A flaw was found in libxslt where the attribute type, atype, flags are modified in a way that corrupts internal memory management. When XSLT functions, such as the key() process, result in tree fragments, this corruption prevents the proper cleanup of ID attributes. As a result, the system may access freed memory, causing crashes or enabling attackers to trigger heap corruption.

## References
- http://seclists.org/fulldisclosure/2025/Aug/0
- http://seclists.org/fulldisclosure/2025/Jul/30
- http://seclists.org/fulldisclosure/2025/Jul/32
- http://seclists.org/fulldisclosure/2025/Jul/35
- http://seclists.org/fulldisclosure/2025/Jul/37
- http://www.openwall.com/lists/oss-security/2025/07/11/2
- https://access.redhat.com/errata/RHBA-2025:12345
- https://access.redhat.com/errata/RHSA-2025:12447
- https://access.redhat.com/errata/RHSA-2025:12450
- https://access.redhat.com/errata/RHSA-2025:13267
- https://access.redhat.com/errata/RHSA-2025:13308
- https://access.redhat.com/errata/RHSA-2025:13309
- https://access.redhat.com/errata/RHSA-2025:13310
- https://access.redhat.com/errata/RHSA-2025:13311
- https://access.redhat.com/errata/RHSA-2025:13312
- https://access.redhat.com/errata/RHSA-2025:13313
- https://access.redhat.com/errata/RHSA-2025:13314
- https://access.redhat.com/errata/RHSA-2025:13335
- https://access.redhat.com/errata/RHSA-2025:13464
- https://access.redhat.com/errata/RHSA-2025:13622
