# [H] CVE-2017-9610

## Summary
Severity: High
Advisory: CVE-2017-9610
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9610
Type: osv

## Details
The xps_load_sfnt_name function in xps/xpsfont.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=d2ab84732936b6e7e5a461dc94344902965e9a06
- http://www.securityfocus.com/bid/99976
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=698025
