# [H] CVE-2020-12783

## Summary
Severity: High
Advisory: CVE-2020-12783
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-11
Source: https://osv.dev/vulnerability/CVE-2020-12783
Type: osv

## Details
Exim through 4.93 has an out-of-bounds read in the SPA authenticator that could result in SPA/NTLM authentication bypass in auths/spa.c and auths/auth-spa.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F6IQQ2SERFUD4WMRSX6XYDNK7Q4GPT7Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M7Z5UG6ZIG32V7M4PP3BCC65C27EWK7G/
- https://bugs.exim.org/show_bug.cgi?id=2571
- https://lists.debian.org/debian-lts-announce/2020/05/msg00017.html
- https://usn.ubuntu.com/4366-1/
- https://www.debian.org/security/2020/dsa-4687
- https://git.exim.org/exim.git/commit/57aa14b216432be381b6295c312065b2fd034f86
- https://git.exim.org/exim.git/commit/a04174dc2a84ae1008c23b6a7109e7fa3fb7b8b0
- http://www.openwall.com/lists/oss-security/2021/05/04/7
