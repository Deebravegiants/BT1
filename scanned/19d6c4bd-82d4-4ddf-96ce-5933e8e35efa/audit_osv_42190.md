# [M] Path Traversal in ATutor

## Summary
Severity: Medium
Advisory: CVE-2026-64967
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-64967
Type: osv

## Details
A path traversal vulnerability in ATutor's error log viewer allows an attacker with administrative privileges to access arbitrary files outside the intended logs directory. This can lead to unauthorized access to sensitive files and other resources accessible to the web server process.






Product is no longer actively supported and the vulnerabilities have not been fixed. Only version 2.2.4 was tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable.

## References
- https://atutor.github.io/
- https://cert.pl/en/posts/2026/08/CVE-2026-64960
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64967.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64967
- https://github.com/atutor/ATutor
