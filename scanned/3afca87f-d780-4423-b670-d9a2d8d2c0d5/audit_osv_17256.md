# [H] CVE-2020-14148

## Summary
Severity: High
Advisory: CVE-2020-14148
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14148
Type: osv

## Details
The Server-Server protocol implementation in ngIRCd before 26~rc2 allows an out-of-bounds access, as demonstrated by the IRC_NJOIN() function.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BJOYV5GHUFJMUVQW3TJKXZ7JPXL4W3ER/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JZRYFJIA6ZKOH7U4K5WH5OL7OKXE4N52/
- https://github.com/ngircd/ngircd/issues/274
- https://github.com/ngircd/ngircd/issues/277
- https://github.com/ngircd/ngircd/pull/276
- https://github.com/ngircd/ngircd/releases/tag/rel-26-rc2
- https://lists.debian.org/debian-lts-announce/2020/06/msg00023.html
- https://github.com/ngircd/ngircd/pull/275
