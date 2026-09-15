# [H] CVE-2016-2056

## Summary
Severity: High
Advisory: CVE-2016-2056
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-2056
Type: osv

## Details
xymond in Xymon 4.1.x, 4.2.x, and 4.3.x before 4.3.25 allow remote authenticated users to execute arbitrary commands via shell metacharacters in the adduser_name argument in (1) web/useradm.c or (2) web/chpasswd.c.

## References
- http://www.securityfocus.com/archive/1/537522/100/0/threaded
- http://packetstormsecurity.com/files/135758/Xymon-4.3.x-Buffer-Overflow-Code-Execution-Information-Disclosure.html
- http://packetstormsecurity.com/files/153620/Xymon-useradm-Command-Execution.html
- http://www.debian.org/security/2016/dsa-3495
- https://sourceforge.net/p/xymon/code/7892/
