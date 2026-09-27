# [C] PopojiCMS 2.0.1 Remote Command Execution via Authenticated Metadata Settings

## Summary
Severity: Critical
Advisory: CVE-2024-58284
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-10
Source: https://osv.dev/vulnerability/CVE-2024-58284
Type: osv

## Details
PopojiCMS 2.0.1 contains an authenticated remote command execution vulnerability that allows administrative users to inject malicious PHP code through the metadata settings endpoint. Attackers can log in and modify the meta content to create a web shell that executes arbitrary system commands through a GET parameter.

## References
- https://github.com/PopojiCMS/PopojiCMS/archive/refs/tags/v2.0.1.zip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58284.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58284
- https://www.popojicms.org/
- https://www.vulncheck.com/advisories/popojicms-remote-command-execution-via-authenticated-metadata-settings
- https://github.com/PopojiCMS/PopojiCMS
- https://www.exploit-db.com/exploits/52022
