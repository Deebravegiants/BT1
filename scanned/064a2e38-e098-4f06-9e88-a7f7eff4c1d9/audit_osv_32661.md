# [M] RIPS Scanner v0.54 Path Traversal

## Summary
Severity: Medium
Advisory: CVE-2025-34126
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-34126
Type: osv

## Details
A path traversal vulnerability exists in RIPS Scanner version 0.54. The vulnerability allows remote attackers to read arbitrary files on the system with the privileges of the web server by sending crafted HTTP GET requests to the 'windows/code.php' script with a manipulated 'file' parameter. This can lead to disclosure of sensitive information.

## References
- https://rips-scanner.sourceforge.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34126.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34126
- https://www.vulncheck.com/advisories/rips-scanner-path-traversal
- https://github.com/robocoder/rips-scanner
- https://codesec.blogspot.com/2015/03/rips-scanner-v-054-local-file-include.html
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/auxiliary/scanner/http/rips_traversal.rb
- https://www.exploit-db.com/exploits/18660
