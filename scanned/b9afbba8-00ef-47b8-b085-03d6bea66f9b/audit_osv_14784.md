# [H] CVE-2019-11413

## Summary
Severity: High
Advisory: CVE-2019-11413
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11413
Type: osv

## Details
An issue was discovered in Artifex MuJS 1.0.5. It has unlimited recursion because the match function in regexp.c lacks a depth check.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3RQXMWEOWCGLOLFBQSXBM3MBN33T4I5H/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/67PMOZV4DLVL2KGU2SV724QL7Y4PKWKU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MFCRO74ORRIVWNVAX2MAMRY3THCTWLQI/
- http://www.securityfocus.com/bid/108093
- https://security.gentoo.org/glsa/202007-52
- https://bugs.ghostscript.com/show_bug.cgi?id=700937
- http://www.ghostscript.com/cgi-bin/findgit.cgi?00d4606c3baf813b7b1c176823b2729bf51002a2
- https://github.com/ccxvii/mujs/commit/00d4606c3baf813b7b1c176823b2729bf51002a2
