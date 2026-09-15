# [H] CVE-2016-10244

## Summary
Severity: High
Advisory: CVE-2016-10244
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/CVE-2016-10244
Type: osv

## Details
The parse_charstrings function in type1/t1load.c in FreeType 2 before 2.7 does not ensure that a font contains a glyph name, which allows remote attackers to cause a denial of service (heap-based buffer over-read) or possibly have unspecified other impact via a crafted file.

## References
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/ChangeLog?h=VER-2-7
- http://www.debian.org/security/2017/dsa-3839
- http://www.securityfocus.com/bid/97405
- http://www.securitytracker.com/id/1038090
- http://www.securitytracker.com/id/1038201
- https://security.gentoo.org/glsa/201706-14
- https://source.android.com/security/bulletin/2017-04-01
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=36
