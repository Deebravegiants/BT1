# [M] Rsync: race condition in rsync handling symbolic links

## Summary
Severity: Medium
Advisory: CVE-2024-12747
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-01-14
Source: https://osv.dev/vulnerability/CVE-2024-12747
Type: osv

## Details
A flaw was found in rsync. This vulnerability arises from a race condition during rsync's handling of symbolic links. Rsync's default behavior when encountering symbolic links is to skip them. If an attacker replaced a regular file with a symbolic link at the right time, it was possible to bypass the default behavior and traverse symbolic links. Depending on the privileges of the rsync process, an attacker could leak sensitive information, potentially leading to privilege escalation.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://kb.cert.org/vuls/id/952657
- https://lists.debian.org/debian-lts-announce/2025/01/msg00008.html
- https://www.kb.cert.org/vuls/id/952657
- https://access.redhat.com/errata/RHBA-2025:6470
- https://access.redhat.com/errata/RHSA-2025:2600
- https://access.redhat.com/errata/RHSA-2025:7050
- https://access.redhat.com/errata/RHSA-2025:8385
- https://access.redhat.com/security/cve/CVE-2024-12747
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12747.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12747
- https://security.netapp.com/advisory/ntap-20250131-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2332968
- https://github.com/RsyncProject/rsync
