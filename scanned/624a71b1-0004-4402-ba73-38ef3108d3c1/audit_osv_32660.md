# [H] ColoradoFTP Server <= 1.3 Build 8 Path Traversal Information Disclosure

## Summary
Severity: High
Advisory: CVE-2025-34110
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-34110
Type: osv

## Details
A directory traversal vulnerability exists in ColoradoFTP Server ≤ 1.3 Build 8 for Windows, allowing unauthenticated attackers to read or write arbitrary files outside the configured FTP root directory. The flaw is due to insufficient sanitation of user-supplied file paths in the FTP GET and PUT command handlers. Exploitation is possible by submitting traversal sequences during FTP operations, enabling access to system-sensitive files. This issue affects only the Windows version of ColoradoFTP.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34110.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34110
- https://www.vulncheck.com/advisories/colorado-ftp-server-path-traversal-information-disclosure
- https://bitbucket.org/nolife/coloradoftp/commits/16a60c4a74ef477cd8c16ca82442eaab2fbe8c86
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/auxiliary/scanner/ftp/colorado_ftp_traversal.rb
- https://www.exploit-db.com/exploits/40231
