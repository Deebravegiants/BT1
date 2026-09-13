# [C] Path Traversal leading to Remote Code Execution in ATutor

## Summary
Severity: Critical
Advisory: CVE-2026-64966
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-64966
Type: osv

## Details
ATutor is vulnerable to a Path Traversal vulnerability in ZIP extraction functionality. An attacker with instructor privileges can upload and extract a specially crafted ZIP archive, causing files to be written outside the intended extraction directory. This allows an attacker to place a server-executable .phtml file in the web root and achieve remote code execution with web server privileges on the underlying server.




Product is no longer actively supported and the vulnerabilities have not been fixed. Only version 2.2.4 was tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable.

## References
- https://atutor.github.io/
- https://cert.pl/en/posts/2026/08/CVE-2026-64960
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64966.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64966
- https://github.com/atutor/ATutor
