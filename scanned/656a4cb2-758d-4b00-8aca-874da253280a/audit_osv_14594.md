# [H] CVE-2019-10193

## Summary
Severity: High
Advisory: CVE-2019-10193
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-10193
Type: osv

## Details
A stack-buffer overflow vulnerability was found in the Redis hyperloglog data structure versions 3.x before 3.2.13, 4.x before 4.0.14 and 5.x before 5.0.4. By corrupting a hyperloglog using the SETRANGE command, an attacker could cause Redis to perform controlled increments of up to 12 bytes past the end of a stack-allocated buffer.

## References
- http://www.securityfocus.com/bid/109290
- https://access.redhat.com/errata/RHSA-2019:1819
- https://access.redhat.com/errata/RHSA-2019:2002
- https://raw.githubusercontent.com/antirez/redis/3.2/00-RELEASENOTES
- https://raw.githubusercontent.com/antirez/redis/4.0/00-RELEASENOTES
- https://raw.githubusercontent.com/antirez/redis/5.0/00-RELEASENOTES
- https://seclists.org/bugtraq/2019/Jul/19
- https://security.gentoo.org/glsa/201908-04
- https://usn.ubuntu.com/4061-1/
- https://www.debian.org/security/2019/dsa-4480
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10193
- https://www.oracle.com/security-alerts/cpujul2020.html
