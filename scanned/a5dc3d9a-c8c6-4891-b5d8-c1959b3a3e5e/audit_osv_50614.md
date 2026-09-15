# [H] CVE-2020-25670

## Summary
Severity: High
Advisory: CVE-2020-25670
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-25670
Type: osv

## Details
A vulnerability was found in Linux Kernel where refcount leak in llcp_sock_bind() causing use-after-free which might lead to privilege escalations.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTVACC6PGS6OSD3EYY7FZUAZT2EUMFH5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VEIEGQXUW37YHZ5MTAZTDCIMHUN26NJS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PW3OASG7OEMHANDWBM5US5WKTOC76KMH/
- https://security.netapp.com/advisory/ntap-20210702-0008/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- http://www.openwall.com/lists/oss-security/2020/11/01/1
- https://www.openwall.com/lists/oss-security/2020/11/01/1
- http://www.openwall.com/lists/oss-security/2021/05/11/4
