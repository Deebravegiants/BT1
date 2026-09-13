# [M] Libxslt: use-after-free with key data stored cross-rvt

## Summary
Severity: Medium
Advisory: BIT-java-2025-10911
Aliases: BIT-java-min-2025-10911, BIT-jre-2025-10911, CVE-2025-10911
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-10911
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.481

## Details
A use-after-free vulnerability was found in libxslt while parsing xsl nodes that may lead to the dereference of expired pointers and application crash.

## References
- https://access.redhat.com/errata/RHSA-2026:11015
- https://access.redhat.com/security/cve/CVE-2025-10911
- https://bugzilla.redhat.com/show_bug.cgi?id=2397838
- https://gitlab.gnome.org/GNOME/libxslt/-/issues/144
- https://gitlab.gnome.org/GNOME/libxslt/-/merge_requests/77
- https://nvd.nist.gov/vuln/detail/CVE-2025-10911
- https://access.redhat.com/errata/RHSA-2026:26355
- https://access.redhat.com/errata/RHSA-2026:28243
- https://access.redhat.com/errata/RHSA-2026:28584
- https://access.redhat.com/errata/RHSA-2026:29807
- https://access.redhat.com/errata/RHSA-2026:29809
- https://access.redhat.com/errata/RHSA-2026:29811
- https://access.redhat.com/errata/RHSA-2026:29814
- https://access.redhat.com/errata/RHSA-2026:29975
- https://access.redhat.com/errata/RHSA-2026:29976
- https://access.redhat.com/errata/RHSA-2026:30847
- https://access.redhat.com/errata/RHSA-2026:33313
- https://access.redhat.com/errata/RHSA-2026:44481
- https://access.redhat.com/errata/RHSA-2026:58981
