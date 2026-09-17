# [M] ProjectSend r1605 Insecure Direct Object Reference File Download Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-53930
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2023-53930
Type: osv

## Details
ProjectSend r1605 contains an insecure direct object reference vulnerability that allows unauthenticated attackers to download private files by manipulating the download ID parameter. Attackers can access any user's private files by changing the 'id' parameter in the download request to process.php.

## References
- https://www.projectsend.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53930.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53930
- https://www.vulncheck.com/advisories/projectsend-insecure-direct-object-reference-file-download-vulnerability
- https://www.exploit-db.com/exploits/51400
