# [C] appRain CMF 4.0.5 Authenticated Remote Code Execution via Filemanager Upload

## Summary
Severity: Critical
Advisory: CVE-2024-58279
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-10
Source: https://osv.dev/vulnerability/CVE-2024-58279
Type: osv

## Details
appRain CMF 4.0.5 contains an authenticated remote code execution vulnerability that allows administrative users to upload malicious PHP files through the filemanager upload endpoint. Attackers can leverage authenticated access to generate a web shell with command execution capabilities by uploading a crafted PHP file to the site's uploads directory.

## References
- https://github.com/apprain/apprain/archive/refs/tags/v4.0.5.zip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58279.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58279
- https://www.apprain.org
- https://www.vulncheck.com/advisories/apprain-cmf-authenticated-remote-code-execution-via-filemanager-upload
- https://www.exploit-db.com/exploits/52041
