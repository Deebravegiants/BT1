# [H] CVE-2015-8080

## Summary
Severity: High
Advisory: CVE-2015-8080
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2015-8080
Type: osv

## Details
Integer overflow in the getnum function in lua_struct.c in Redis 2.8.x before 2.8.24 and 3.0.x before 3.0.6 allows context-dependent attackers with permission to run Lua code in a Redis session to cause a denial of service (memory corruption and application crash) or possibly bypass intended sandbox restrictions via a large number, which triggers a stack-based buffer overflow.

## References
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00126.html
- http://rhn.redhat.com/errata/RHSA-2016-0095.html
- http://rhn.redhat.com/errata/RHSA-2016-0096.html
- http://rhn.redhat.com/errata/RHSA-2016-0097.html
- http://www.debian.org/security/2015/dsa-3412
- http://www.openwall.com/lists/oss-security/2015/11/06/2
- http://www.openwall.com/lists/oss-security/2015/11/06/4
- http://www.securityfocus.com/bid/77507
- https://github.com/antirez/redis/issues/2855
- https://raw.githubusercontent.com/antirez/redis/2.8/00-RELEASENOTES
- https://raw.githubusercontent.com/antirez/redis/3.0/00-RELEASENOTES
- https://security.gentoo.org/glsa/201702-16
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00126.html
- http://www.openwall.com/lists/oss-security/2015/11/06/2
- http://www.openwall.com/lists/oss-security/2015/11/06/4
- https://github.com/antirez/redis/issues/2855
- https://github.com/antirez/redis/issues/2855
- https://github.com/antirez/redis/issues/2855
