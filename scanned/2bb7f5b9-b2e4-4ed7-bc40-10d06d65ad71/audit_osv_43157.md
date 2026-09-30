# [C] dulldusk phpfm - Unauthenticated Remote Code Execution via Unrestricted PHP File Upload

## Summary
Severity: Critical
Advisory: CVE-2026-72592
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72592
Type: osv

## Details
An unrestricted file upload vulnerability in dulldusk/phpfm through 1.8.0 allows an unauthenticated remote attacker to execute arbitrary PHP code on the server. The application ships with an empty upload extension filter ( = array) and no authentication enabled by default (auth_pass is empty string), allowing an unauthenticated attacker to upload a PHP webshell and execute it by browsing to the uploaded path.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72592.json
- https://github.com/dulldusk/phpfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72592
- https://github.com/dulldusk/phpfm/blob/master/index.php
