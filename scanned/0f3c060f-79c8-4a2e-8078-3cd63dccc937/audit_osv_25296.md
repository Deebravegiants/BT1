# [M] CVE-2023-33285

## Summary
Severity: Medium
Advisory: CVE-2023-33285
CVSS: 5.3 (CVSS:3.1/AC:L/AV:N/A:L/C:N/I:N/PR:N/S:U/UI:N)
Published: 2023-05-22
Source: https://osv.dev/vulnerability/CVE-2023-33285
Type: osv

## Details
An issue was discovered in Qt 5.x before 5.15.14, 6.x before 6.2.9, and 6.3.x through 6.5.x before 6.5.1. QDnsLookup has a buffer over-read via a crafted reply from a DNS server.

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/477644
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33285.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-33285
- https://lists.debian.org/debian-lts-announce/2024/04/msg00027.html
