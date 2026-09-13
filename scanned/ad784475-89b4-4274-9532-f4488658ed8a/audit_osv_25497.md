# [H] Sssd: race condition during authorization leads to gpo policies functioning inconsistently

## Summary
Severity: High
Advisory: CVE-2023-3758
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2023-3758
Type: osv

## Details
A race condition flaw was found in sssd where the GPO policy is not consistently applied for authenticated users. This may lead to improper authorization issues, granting or denying access to resources inappropriately.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RV3HIZI3SURBUQKSOOL3XE64OOBQ2HTK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XEP62IDS7A55D5UHM6GH7QZ7SQFOAPVF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XMORAO2BDDA5YX4ZLMXDZ7SM6KU47SY5/
- https://sssd.io/
- https://access.redhat.com/errata/RHSA-2024:1919
- https://access.redhat.com/errata/RHSA-2024:1920
- https://access.redhat.com/errata/RHSA-2024:1921
- https://access.redhat.com/errata/RHSA-2024:1922
- https://access.redhat.com/errata/RHSA-2024:2571
- https://access.redhat.com/errata/RHSA-2024:3270
- https://access.redhat.com/security/cve/CVE-2023-3758
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3758.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3758
- https://bugzilla.redhat.com/show_bug.cgi?id=2223762
- https://github.com/SSSD/sssd/pull/7302
