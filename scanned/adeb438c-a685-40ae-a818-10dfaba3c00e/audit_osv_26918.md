# [M] Opensc: side-channel leaks while stripping encryption pkcs#1 padding

## Summary
Severity: Medium
Advisory: CVE-2023-5992
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2023-5992
Type: osv

## Details
A vulnerability was found in OpenSC where PKCS#1 encryption padding removal is not implemented as side-channel resistant. This issue may result in the potential leak of private data.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/OpenSC/OpenSC/wiki/CVE-2023-5992
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OWIZ5ZLO5ECYPLSTESCF7I7PQO5X6ZSU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RJI2FWLY24EOPALQ43YPQEZMEP3APPPI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UECKC7X4IM4YZQ5KRQMNBNKNOXLZC7RZ/
- https://www.usenix.org/system/files/usenixsecurity24-shagam.pdf
- https://access.redhat.com/errata/RHSA-2024:0966
- https://access.redhat.com/errata/RHSA-2024:0967
- https://access.redhat.com/security/cve/CVE-2023-5992
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5992.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5992
- https://bugzilla.redhat.com/show_bug.cgi?id=2248685
