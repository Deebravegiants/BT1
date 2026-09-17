# [H] CVE-2017-9618

## Summary
Severity: High
Advisory: CVE-2017-9618
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9618
Type: osv

## Details
The xps_load_sfnt_name function in xps/xpsfont.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=3c2aebbedd37fab054e80f2e315de07d7e9b5bdb
- http://www.securityfocus.com/bid/99993
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=698044
