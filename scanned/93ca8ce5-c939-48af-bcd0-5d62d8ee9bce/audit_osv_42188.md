# [C] Remote Code Execution via Unrestricted File Upload in ATutor

## Summary
Severity: Critical
Advisory: CVE-2026-64960
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-64960
Type: osv

## Details
ATutor Gameme module allows users to upload files of any type and extension without restriction. Due to improper handling of file uploads, files are stored in a web-accessible location before their content is validated. An authenticated attacker who knows a valid course_id can upload a server-executable malicious script. The uploaded file can then be requested over HTTP, resulting in remote code execution as the web server process user. In most cases, course_id=0 can be used, as it commonly represents the global context.




Product is no longer actively supported and the vulnerabilities have not been fixed. Only version 2.2.4 was tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable.

## References
- https://atutor.github.io/
- https://cert.pl/en/posts/2026/08/CVE-2026-64960
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64960.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64960
- https://github.com/atutor/ATutor
