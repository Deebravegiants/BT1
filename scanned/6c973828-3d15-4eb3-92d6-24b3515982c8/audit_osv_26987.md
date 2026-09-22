# [M] Systemd-resolved: unsigned name response in signed zone is not refused when dnssec=yes

## Summary
Severity: Medium
Advisory: CVE-2023-7008
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-12-23
Source: https://osv.dev/vulnerability/CVE-2023-7008
Type: osv

## Details
A vulnerability was found in systemd-resolved. This issue may allow systemd-resolved to accept records of DNSSEC-signed domains even when they have no signature, allowing man-in-the-middles (or the upstream DNS resolver) to manipulate records.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/09/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4GMDEG5PKONWNHOEYSUDRT6JEOISRMN2/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QHNBXGKJWISJETTTDTZKTBFIBJUOSLKL/
- https://access.redhat.com/errata/RHSA-2024:2463
- https://access.redhat.com/errata/RHSA-2024:3203
- https://access.redhat.com/security/cve/CVE-2023-7008
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7008.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7008
- https://security.netapp.com/advisory/ntap-20241122-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2222261
- https://bugzilla.redhat.com/show_bug.cgi?id=2222672
- https://github.com/systemd/systemd/issues/25676
