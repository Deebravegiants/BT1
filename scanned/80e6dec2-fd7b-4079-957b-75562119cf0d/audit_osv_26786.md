# [C] Dotclear 2.25.3 Authenticated Remote Code Execution via File Upload

## Summary
Severity: Critical
Advisory: CVE-2023-53952
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2023-53952
Type: osv

## Details
Dotclear 2.25.3 contains a remote code execution vulnerability that allows authenticated attackers to upload malicious PHP files with .phar extension through the blog post creation interface. Attackers can upload files containing PHP system commands that execute when the uploaded file is accessed, enabling arbitrary code execution on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53952.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53952
- https://www.vulncheck.com/advisories/dotclear-authenticated-remote-code-execution-via-file-upload
- https://dotclear.org/
- https://www.exploit-db.com/exploits/51353
