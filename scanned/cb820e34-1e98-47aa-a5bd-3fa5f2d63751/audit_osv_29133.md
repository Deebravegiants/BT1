# [H] CVE-2024-39936

## Summary
Severity: High
Advisory: CVE-2024-39936
CVSS: 8.6 (CVSS:3.1/AC:L/AV:N/A:N/C:H/I:N/PR:N/S:C/UI:N)
Published: 2024-07-04
Source: https://osv.dev/vulnerability/CVE-2024-39936
Type: osv

## Details
An issue was discovered in HTTP2 in Qt before 5.15.18, 6.x before 6.2.13, 6.3.x through 6.5.x before 6.5.7, and 6.6.x through 6.7.x before 6.7.3. Code to make security-relevant decisions about an established connection may execute too early, because the encrypted() signal has not yet been emitted and processed..

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/571601
- https://lists.debian.org/debian-lts-announce/2025/11/msg00031.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39936.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39936
