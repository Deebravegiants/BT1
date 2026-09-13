# [H] CVE-2018-6383

## Summary
Severity: High
Advisory: CVE-2018-6383
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-29
Source: https://osv.dev/vulnerability/CVE-2018-6383
Type: osv

## Details
Monstra CMS through 3.0.4 has an incomplete "forbidden types" list that excludes .php (and similar) file extensions but not the .pht or .phar extension, which allows remote authenticated Admins or Editors to execute arbitrary PHP code by uploading a file, a different vulnerability than CVE-2017-18048.

## References
- https://github.com/monstra-cms/monstra/issues/429
- http://packetstormsecurity.com/files/162968/Monstra-CMS-3.0.4-Remote-Code-Execution.html
- https://github.com/Hacker5preme/Exploits/tree/main/CVE-2018-6383-Exploit
