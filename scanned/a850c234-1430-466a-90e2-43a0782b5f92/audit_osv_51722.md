# [M] CVE-2021-38165

## Summary
Severity: Medium
Advisory: CVE-2021-38165
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/CVE-2021-38165
Type: osv

## Details
Lynx through 2.8.9 mishandles the userinfo subcomponent of a URI, which allows remote attackers to discover cleartext credentials because they may appear in SNI data.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7YMUHFJJWTZ6HBHTYXVDPNZINGGURHDW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K6PZF7JNTFCOJ62HXZG4Q2NEHSZ6IO2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VKNK7GQBJBUBMJVNKVC7RTCYWUYMFJQW/
- http://www.openwall.com/lists/oss-security/2021/08/07/9
- https://lists.debian.org/debian-lts-announce/2021/08/msg00010.html
- https://www.debian.org/security/2021/dsa-4953
- https://www.openwall.com/lists/oss-security/2021/08/07/1
- http://www.openwall.com/lists/oss-security/2021/08/07/11
- http://www.openwall.com/lists/oss-security/2021/08/07/12
- https://github.com/w3c/libwww/blob/f010b4cc58d32f34b162f0084fe093f7097a61f0/Library/src/HTParse.c#L118
- https://lynx.invisible-island.net/current/CHANGES.html
- https://bugs.debian.org/991971
- https://www.openwall.com/lists/oss-security/2021/08/07/11
