# [C] ElkArte Forum 1.1.9 Authenticated Remote Code Execution via Theme Upload

## Summary
Severity: Critical
Advisory: CVE-2024-58295
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2024-58295
Type: osv

## Details
ElkArte Forum 1.1.9 contains a remote code execution vulnerability that allows authenticated administrators to upload malicious PHP files through the theme installation process. Attackers can upload a ZIP archive with a PHP file containing system commands, which can then be executed by accessing the uploaded file in the theme directory.

## References
- https://github.com/elkarte/Elkarte/releases/download/v1.1.9/ElkArte_v1-1-9_install.zip
- https://www.elkarte.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58295.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58295
- https://www.vulncheck.com/advisories/elkarte-forum-authenticated-remote-code-execution-via-theme-upload
- https://www.exploit-db.com/exploits/52026
