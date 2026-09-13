# [M] CVE-2024-33870

## Summary
Severity: Medium
Advisory: CVE-2024-33870
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-33870
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. There is path traversal (via a crafted PostScript document) to arbitrary files if the current directory is in the permitted paths. For example, there can be a transformation of ../../foo to ./../../foo and this will grant access if ./ is permitted.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707686
- https://www.openwall.com/lists/oss-security/2024/06/28/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33870.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33870
