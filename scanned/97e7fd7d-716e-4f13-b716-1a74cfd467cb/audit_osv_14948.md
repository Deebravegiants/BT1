# [C] CVE-2019-12524

## Summary
Severity: Critical
Advisory: CVE-2019-12524
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2019-12524
Type: osv

## Details
An issue was discovered in Squid through 4.7. When handling requests from users, Squid checks its rules to see if the request should be denied. Squid by default comes with rules to block access to the Cache Manager, which serves detailed server information meant for the maintainer. This rule is implemented via url_regex. The handler for url_regex rules URL decodes an incoming request. This allows an attacker to encode their URL to bypass the url_regex check, and gain access to the blocked resource.

## References
- https://gitlab.com/jeriko.one/security/-/blob/master/squid/CVEs/CVE-2019-12524.txt
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20210205-0006/
- https://usn.ubuntu.com/4446-1/
- https://www.debian.org/security/2020/dsa-4682
