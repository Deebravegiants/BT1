# [C] Blackcat CMS 1.4 Remote Code Execution via Jquery Plugin Manager

## Summary
Severity: Critical
Advisory: CVE-2023-53892
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2023-53892
Type: osv

## Details
Blackcat CMS 1.4 contains a remote code execution vulnerability that allows authenticated administrators to upload malicious PHP files through the jquery plugin manager. Attackers can upload a zip file with a PHP shell script and execute arbitrary system commands by accessing the uploaded plugin's PHP file with a 'code' parameter.

## References
- https://blackcat-cms.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53892.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53892
- https://www.vulncheck.com/advisories/blackcat-cms-remote-code-execution-via-jquery-plugin-manager
- https://www.exploit-db.com/exploits/51605
