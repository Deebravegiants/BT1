# [H] CVE-2016-5399

## Summary
Severity: High
Advisory: CVE-2016-5399
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-21
Source: https://osv.dev/vulnerability/CVE-2016-5399
Type: osv

## Details
The bzread function in ext/bz2/bz2.c in PHP before 5.5.38, 5.6.x before 5.6.24, and 7.x before 7.0.9 allows remote attackers to cause a denial of service (out-of-bounds write) or execute arbitrary code via a crafted bz2 archive.

## References
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2598.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.securityfocus.com/archive/1/538966/100/0/threaded
- http://www.securityfocus.com/bid/92051
- http://www.securitytracker.com/id/1036430
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1358395
- http://packetstormsecurity.com/files/137998/PHP-7.0.8-5.6.23-5.5.37-bzread-OOB-Write.html
- http://seclists.org/fulldisclosure/2016/Jul/72
- http://www.openwall.com/lists/oss-security/2016/07/21/1
- https://bugs.php.net/bug.php?id=72613
- https://www.exploit-db.com/exploits/40155/
