# [C] Xerte Online Toolkits <= 3.14 Unauthenticated Template Import Arbitrary File Upload Leading to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-32985
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32985
Type: osv

## Details
Xerte Online Toolkits versions 3.14 and earlier contain an unauthenticated arbitrary file upload vulnerability in the template import functionality that allows remote attackers to execute arbitrary code by uploading a crafted ZIP archive containing malicious PHP payloads. Attackers can bypass authentication checks in the import.php file to upload a template archive with PHP code in the media directory, which gets extracted to a web-accessible path where the malicious PHP can be directly accessed and executed under the web server context.

## References
- https://xot.xerte.org.uk/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32985.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32985
- https://packetstorm.news/files/id/216288/
