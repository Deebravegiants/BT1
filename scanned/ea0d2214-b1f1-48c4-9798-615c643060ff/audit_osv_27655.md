# [C] Bludit - Remote Code Execution (RCE) through File API

## Summary
Severity: Critical
Advisory: CVE-2024-24550
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-24550
Type: osv

## Details
A security vulnerability has been identified in Bludit, allowing attackers with knowledge of the API token to upload arbitrary files through the File API which leads to arbitrary code execution on the server. This vulnerability arises from improper handling of file uploads, enabling malicious actors to upload and execute PHP files.

## References
- https://github.com/bludit/bludit/
- https://www.bludit.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24550.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24550
- https://www.redguard.ch/blog/2024/06/20/security-advisory-bludit/
