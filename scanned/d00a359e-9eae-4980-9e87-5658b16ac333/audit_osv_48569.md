# [H] CVE-2017-9620

## Summary
Severity: High
Advisory: CVE-2017-9620
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9620
Type: osv

## Details
The xps_select_font_encoding function in xps/xpsfont.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted document, related to the xps_encode_font_char_imp function.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=3ee55637480d5e319a5de0481b01c3346855cbc9
- http://www.securityfocus.com/bid/99990
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=698050
