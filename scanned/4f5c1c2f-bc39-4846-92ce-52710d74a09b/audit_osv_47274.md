# [C] CVE-2016-2054

## Summary
Severity: Critical
Advisory: CVE-2016-2054
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-2054
Type: osv

## Details
Multiple buffer overflows in xymond/xymond.c in xymond in Xymon 4.1.x, 4.2.x, and 4.3.x before 4.3.25 allow remote attackers to execute arbitrary code or cause a denial of service (daemon crash) via a long filename, involving handling a "config" command.

## References
- http://packetstormsecurity.com/files/135758/Xymon-4.3.x-Buffer-Overflow-Code-Execution-Information-Disclosure.html
- http://www.securityfocus.com/archive/1/537522/100/0/threaded
- http://lists.xymon.com/archive/2016-February/042986.html
- http://www.debian.org/security/2016/dsa-3495
- https://sourceforge.net/p/xymon/code/7859/
- https://sourceforge.net/p/xymon/code/7860/
