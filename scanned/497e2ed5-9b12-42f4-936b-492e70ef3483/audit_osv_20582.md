# [M] CVE-2021-3531

## Summary
Severity: Medium
Advisory: CVE-2021-3531
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-05-18
Source: https://osv.dev/vulnerability/CVE-2021-3531
Type: osv

## Details
A flaw was found in the Red Hat Ceph Storage RGW in versions before 14.2.21. When processing a GET Request for a swift URL that ends with two slashes it can cause the rgw to crash, resulting in a denial of service. The greatest threat to the system is of availability.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FX5ZHI5L7FOHXOSEV3TYBAL66DMLJ7V5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LPCJN2YDZCBMF4FOJXSTAADKFGEQEO7O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZRUNDH2TJRZRWL3DCH2PQ6KROWTPQ7AJ/
- http://www.openwall.com/lists/oss-security/2021/05/14/5
- http://www.openwall.com/lists/oss-security/2021/05/17/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1955326
