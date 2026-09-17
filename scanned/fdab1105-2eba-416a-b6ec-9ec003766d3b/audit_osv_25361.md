# [M] CVE-2023-34410

## Summary
Severity: Medium
Advisory: CVE-2023-34410
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-06-05
Source: https://osv.dev/vulnerability/CVE-2023-34410
Type: osv

## Details
An issue was discovered in Qt before 5.15.15, 6.x before 6.2.9, and 6.3.x through 6.5.x before 6.5.2. Certificate validation for TLS does not always consider whether the root of a chain is a configured CA certificate.

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/477560
- https://codereview.qt-project.org/c/qt/qtbase/+/480002
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34410.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UE3IHQZCEUFVOPWG75V2HDKXNUZBB4FX/
- https://nvd.nist.gov/vuln/detail/CVE-2023-34410
- https://lists.debian.org/debian-lts-announce/2023/08/msg00028.html
