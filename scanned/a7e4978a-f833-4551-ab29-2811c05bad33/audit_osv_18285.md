# [H] CVE-2020-25790

## Summary
Severity: High
Advisory: CVE-2020-25790
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-19
Source: https://osv.dev/vulnerability/CVE-2020-25790
Type: osv

## Details
Typesetter CMS 5.x through 5.1 allows admins to upload and execute arbitrary PHP code via a .php file inside a ZIP archive. NOTE: the vendor disputes the significance of this report because "admins are considered trustworthy"; however, the behavior "contradicts our security policy" and is being fixed for 5.2

## References
- http://packetstormsecurity.com/files/159503/Typesetter-CMS-5.1-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2020/Oct/11
- https://github.com/Typesetter/Typesetter/issues/674
- http://packetstormsecurity.com/files/159615/Typesetter-CMS-5.1-Remote-Code-Execution.html
