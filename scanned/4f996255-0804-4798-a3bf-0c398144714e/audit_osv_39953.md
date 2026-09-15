# [C] CVE-2026-48700

## Summary
Severity: Critical
Advisory: CVE-2026-48700
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/AU:N/R:I/V:D/RE:M/U:Clear)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-48700
Type: osv

## Details
An issue was discovered in all versions of PCManFM-Qt starting from 1.1.0. When a regular file's path is passed as a URI in an org.freedesktop.FileManager1.ShowFolders D-Bus method call, PCManFM-Qt delegates to a different program (based on the file type) without user confirmation. This could be used to achieve code execution or circumvent network namespace restrictions. NOTE: those outcomes are potentially unwanted by most users; however, the behavior of the product does comply with the applicable specification, and a simplistic solution (ensuring that the URI does not name a regular file) may have adverse consequences for I/O.

## References
- http://www.openwall.com/lists/oss-security/2026/05/24/6
- https://www.openwall.com/lists/oss-security/2026/05/19/1
- https://www.openwall.com/lists/oss-security/2026/05/20/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48700.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48700
- https://github.com/lxqt/pcmanfm-qt
- https://github.com/lxqt/pcmanfm-qt/releases
