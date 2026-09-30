# [M] CVE-2023-32762

## Summary
Severity: Medium
Advisory: CVE-2023-32762
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-05-28
Source: https://osv.dev/vulnerability/CVE-2023-32762
Type: osv

## Details
An issue was discovered in Qt before 5.15.14, 6.x before 6.2.9, and 6.3.x through 6.5.x before 6.5.1. Qt Network incorrectly parses the strict-transport-security (HSTS) header, allowing unencrypted connections to be established, even when explicitly prohibited by the server. This happens if the case used for this header does not exactly match.

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/476140
- https://lists.qt-project.org/pipermail/announce/2023-May/000414.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32762.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32762
- https://github.com/qt/qtbase/commit/1b736a815be0222f4b24289cf17575fc15707305
- https://lists.debian.org/debian-lts-announce/2024/04/msg00027.html
