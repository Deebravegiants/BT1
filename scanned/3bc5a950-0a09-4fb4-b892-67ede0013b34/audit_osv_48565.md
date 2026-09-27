# [H] CVE-2017-9611

## Summary
Severity: High
Advisory: CVE-2017-9611
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9611
Type: osv

## Details
The Ins_MIRP function in base/ttinterp.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=c7c55972758a93350882c32147801a3485b010fe
- http://www.securityfocus.com/bid/99975
- https://security.gentoo.org/glsa/201811-12
- http://www.debian.org/security/2017/dsa-3986
- https://bugs.ghostscript.com/show_bug.cgi?id=698024
