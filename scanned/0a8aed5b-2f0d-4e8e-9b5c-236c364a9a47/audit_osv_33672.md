# [C] FreeScout Vulnerable to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-48390
Aliases: GHSA-5324-cw55-gwj5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-48390
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.178, FreeScout is vulnerable to code injection due to insufficient validation of user input in the php_path parameter. The backticks characters are not removed, as well as tabulation is not removed. When checking user input, the file_exists function is also called to check for the presence of such a file (folder) in the file system. A user with the administrator role can create a translation for the language, which will create a folder in the file system. Further in tools.php, the user can specify the path to this folder as php_path, which will lead to the execution of code in backticks. This issue has been patched in version 1.8.178.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48390.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-5324-cw55-gwj5
- https://nvd.nist.gov/vuln/detail/CVE-2025-48390
- https://github.com/freescout-help-desk/freescout/commit/fb33d672a2d67f5a2b3cf69c80945267f17908b2
