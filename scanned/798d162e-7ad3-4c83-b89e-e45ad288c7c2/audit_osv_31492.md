# [M] Libvirt: denial of service in xml parsing

## Summary
Severity: Medium
Advisory: CVE-2025-12748
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-11
Source: https://osv.dev/vulnerability/CVE-2025-12748
Type: osv

## Details
A flaw was discovered in libvirt in the XML file processing. More specifically, the parsing of user provided XML files was performed before the ACL checks. A malicious user with limited permissions could exploit this flaw by submitting a specially crafted XML file, causing libvirt to allocate too much memory on the host. The excessive memory consumption could lead to a libvirt process crash on the host, resulting in a denial-of-service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:18326
- https://access.redhat.com/errata/RHSA-2026:18748
- https://access.redhat.com/security/cve/CVE-2025-12748
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12748.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-12748
- https://bugzilla.redhat.com/show_bug.cgi?id=2413801
- https://gitlab.com/libvirt/libvirt
