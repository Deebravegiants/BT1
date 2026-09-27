# [H] CVE-2017-9739

## Summary
Severity: High
Advisory: CVE-2017-9739
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9739
Type: osv

## Details
The Ins_JMPR function in base/ttinterp.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=c501a58f8d5650c8ba21d447c0d6f07eafcb0f15
- http://www.debian.org/security/2017/dsa-3986
- http://www.securityfocus.com/bid/99987
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=698063
