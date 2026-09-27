# [C] CVE-2019-12519

## Summary
Severity: Critical
Advisory: CVE-2019-12519
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2019-12519
Type: osv

## Details
An issue was discovered in Squid through 4.7. When handling the tag esi:when when ESI is enabled, Squid calls ESIExpression::Evaluate. This function uses a fixed stack buffer to hold the expression while it's being evaluated. When processing the expression, it could either evaluate the top of the stack, or add a new member to the stack. When adding a new member, there is no check to ensure that the stack won't overflow.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00018.html
- http://www.openwall.com/lists/oss-security/2020/04/23/1
- https://gitlab.com/jeriko.one/security/-/blob/master/squid/CVEs/CVE-2019-12519.txt
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://security.gentoo.org/glsa/202005-05
- https://security.netapp.com/advisory/ntap-20210205-0006/
- https://usn.ubuntu.com/4356-1/
- https://www.debian.org/security/2020/dsa-4682
