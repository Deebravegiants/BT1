# [M] CVE-2025-30348

## Summary
Severity: Medium
Advisory: CVE-2025-30348
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2025-03-21
Source: https://osv.dev/vulnerability/CVE-2025-30348
Type: osv

## Details
encodeText in QDom in Qt before 6.8.0 has a complex algorithm involving XML string copy and inline replacement of parts of a string (with relocation of later data).

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/581442
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30348.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30348
