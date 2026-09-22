# [C] Adminer and AdminerEvo vulnerable to directory traversal and file upload

## Summary
Severity: Critical
Advisory: CVE-2023-45197
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L/AU:Y)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2023-45197
Type: osv

## Details
The file upload plugin in Adminer and AdminerEvo allows an attacker to upload a file with a table name of “..” to the root of the Adminer directory. The attacker can effectively guess the name of the uploaded file and execute it. Adminer is no longer supported, but this issue was fixed in AdminerEvo version 4.8.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45197.json
- https://github.com/adminerevo/adminerevo/releases/tag/v4.8.3
- https://nvd.nist.gov/vuln/detail/CVE-2023-45197
- https://github.com/adminerevo/adminerevo/commit/1cc06d6a1005fd833fa009701badd5641627a1d4
- https://github.com/adminerevo/adminerevo
