# [M] CVE-2024-33869

## Summary
Severity: Medium
Advisory: CVE-2024-33869
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-33869
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. Path traversal and command execution can occur (via a crafted PostScript document) because of path reduction in base/gpmisc.c. For example, restrictions on use of %pipe% can be bypassed via the aa/../%pipe%command# output filename.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707691
- https://www.openwall.com/lists/oss-security/2024/06/28/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33869.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33869
