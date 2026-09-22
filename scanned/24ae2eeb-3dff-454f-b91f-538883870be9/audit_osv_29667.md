# [M] ZDI-CAN-24744: Mintty Path Conversion Improper Input Validation Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-45301
Aliases: GHSA-jf4m-m6rv-p6c5
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2024-45301
Type: osv

## Details
Mintty is a terminal emulator for Cygwin, MSYS, and WSL. In versions 2.3.6 through 3.7.4, several escape sequences can cause the mintty process to access a file in a specific path. It is triggered by simply printing them out on bash. An attacker can specify an arbitrary network path, negotiate an ntlm hash out of the victim's machine to an attacker controlled remote host. An attacker can use password cracking tools or NetNTLMv2 hashes to Pass the Hash. Version 3.7.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45301.json
- https://github.com/mintty/mintty/security/advisories/GHSA-jf4m-m6rv-p6c5
- https://nvd.nist.gov/vuln/detail/CVE-2024-45301
