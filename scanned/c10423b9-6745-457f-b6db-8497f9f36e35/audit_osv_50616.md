# [M] CVE-2020-25673

## Summary
Severity: Medium
Advisory: CVE-2020-25673
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-25673
Type: osv

## Details
A vulnerability was found in Linux kernel where non-blocking socket in llcp_sock_connect() leads to leak and eventually hanging-up the system.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PW3OASG7OEMHANDWBM5US5WKTOC76KMH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTVACC6PGS6OSD3EYY7FZUAZT2EUMFH5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VEIEGQXUW37YHZ5MTAZTDCIMHUN26NJS/
- https://security.netapp.com/advisory/ntap-20210702-0008/
- https://www.openwall.com/lists/oss-security/2020/11/01/1
- http://www.openwall.com/lists/oss-security/2020/11/01/1
