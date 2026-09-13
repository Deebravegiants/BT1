# [H] Gimp: multiple use after free in xcf parser

## Summary
Severity: High
Advisory: CVE-2025-48798
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-48798
Type: osv

## Details
A flaw was found in GIMP when processing XCF image files. If a user opens one of these image files that has been specially crafted by an attacker, GIMP can be tricked into making serious memory errors, potentially leading to crashes and causing use-after-free issues.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/10/msg00022.html
- https://www.gimp.org/
- https://access.redhat.com/errata/RHSA-2025:9162
- https://access.redhat.com/errata/RHSA-2025:9165
- https://access.redhat.com/errata/RHSA-2025:9308
- https://access.redhat.com/errata/RHSA-2025:9309
- https://access.redhat.com/errata/RHSA-2025:9310
- https://access.redhat.com/errata/RHSA-2025:9314
- https://access.redhat.com/errata/RHSA-2025:9315
- https://access.redhat.com/errata/RHSA-2025:9316
- https://access.redhat.com/errata/RHSA-2025:9501
- https://access.redhat.com/errata/RHSA-2025:9569
- https://access.redhat.com/security/cve/CVE-2025-48798
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48798.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48798
- https://bugzilla.redhat.com/show_bug.cgi?id=2368557
- https://gitlab.gnome.org/GNOME/gimp/-/issues/11822
