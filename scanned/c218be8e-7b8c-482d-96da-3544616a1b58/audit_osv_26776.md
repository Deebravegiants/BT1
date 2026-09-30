# [C] Coppermine Gallery 1.6.25 Remote Code Execution via Plugin Upload

## Summary
Severity: Critical
Advisory: CVE-2023-53868
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2023-53868
Type: osv

## Details
Coppermine Gallery 1.6.25 contains a remote code execution vulnerability that allows authenticated attackers to upload malicious PHP files through the plugin manager. Attackers can upload a zipped PHP file with system commands to the plugin directory and execute arbitrary code by accessing the uploaded plugin script.

## References
- https://web.archive.org/web/20240101151648/https://coppermine-gallery.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53868.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53868
- https://www.vulncheck.com/advisories/coppermine-gallery-remote-code-execution-via-plugin-upload
- https://www.exploit-db.com/exploits/51738
