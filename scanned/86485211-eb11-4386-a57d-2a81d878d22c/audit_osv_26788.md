# [C] ProjectSend r1605 Remote Code Execution via File Extension Manipulation

## Summary
Severity: Critical
Advisory: CVE-2023-53980
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2023-53980
Type: osv

## Details
ProjectSend r1605 contains a remote code execution vulnerability that allows attackers to upload malicious files by manipulating file extensions. Attackers can upload shell scripts with disguised extensions through the upload.process.php endpoint to execute arbitrary commands on the server.

## References
- https://www.projectsend.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53980.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53980
- https://www.vulncheck.com/advisories/projectsend-remote-code-execution-via-file-extension-manipulation
- https://www.exploit-db.com/exploits/51238
