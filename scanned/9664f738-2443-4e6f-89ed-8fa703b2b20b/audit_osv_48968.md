# [H] CVE-2018-19134

## Summary
Severity: High
Advisory: CVE-2018-19134
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-19134
Type: osv

## Details
In Artifex Ghostscript through 9.25, the setpattern operator did not properly validate certain types. A specially crafted PostScript document could exploit this to crash Ghostscript or, possibly, execute arbitrary code in the context of the Ghostscript process. This is a type confusion issue because of failure to check whether the Implementation of a pattern dictionary was a structure type.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=693baf02152119af6e6afd30bb8ec76d14f84bbf
- http://www.securityfocus.com/bid/106278
- https://access.redhat.com/errata/RHSA-2018:3834
- https://lists.debian.org/debian-lts-announce/2018/12/msg00019.html
- https://www.ghostscript.com/doc/9.26/News.htm
- https://bugs.ghostscript.com/show_bug.cgi?id=700141
- https://semmle.com/news/semmle-discovers-severe-vulnerability-ghostscript-postscript-pdf
