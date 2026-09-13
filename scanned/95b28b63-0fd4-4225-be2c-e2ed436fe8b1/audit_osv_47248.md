# [H] CVE-2016-1951

## Summary
Severity: High
Advisory: CVE-2016-1951
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-1951
Type: osv

## Details
Multiple integer overflows in io/prprf.c in Mozilla Netscape Portable Runtime (NSPR) before 4.12 allow remote attackers to cause a denial of service (buffer overflow) or possibly have unspecified other impact via a long string to a PR_*printf function.

## References
- https://hg.mozilla.org/projects/nspr/rev/96381e3aaae2
- http://www.securityfocus.com/bid/92385
- http://www.securitytracker.com/id/1036590
- http://www.ubuntu.com/usn/USN-3023-1
- https://bugzilla.mozilla.org/show_bug.cgi?id=1174015
- https://groups.google.com/forum/message/raw?msg=mozilla.dev.tech.nspr/dV4MyMsg6jw/hhWcXOgJDQAJ
