# [H] CVE-2019-11412

## Summary
Severity: High
Advisory: CVE-2019-11412
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11412
Type: osv

## Details
An issue was discovered in Artifex MuJS 1.0.5. jscompile.c can cause a denial of service (invalid stack-frame jump) because it lacks an ENDTRY opcode call.

## References
- http://www.securityfocus.com/bid/108093
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3RQXMWEOWCGLOLFBQSXBM3MBN33T4I5H/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/67PMOZV4DLVL2KGU2SV724QL7Y4PKWKU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MFCRO74ORRIVWNVAX2MAMRY3THCTWLQI/
- https://security.gentoo.org/glsa/202007-52
- https://bugs.ghostscript.com/show_bug.cgi?id=700947
- http://www.ghostscript.com/cgi-bin/findgit.cgi?1e5479084bc9852854feb1ba9bf68b52cd127e02
- https://github.com/ccxvii/mujs/commit/1e5479084bc9852854feb1ba9bf68b52cd127e02
