# [H] CVE-2014-9747

## Summary
Severity: High
Advisory: CVE-2014-9747
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2014-9747
Type: osv

## Details
The t42_parse_encoding function in type42/t42parse.c in FreeType before 2.5.4 does not properly update the current position for immediates-only mode, which allows remote attackers to cause a denial of service (infinite loop) via a Type42 font.

## References
- http://www.debian.org/security/2015/dsa-3370
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/src/type42/t42parse.c?id=8b281f83e8516535756f92dbf90940ac44bd45e1
- http://www.openwall.com/lists/oss-security/2015/09/11/4
- http://www.openwall.com/lists/oss-security/2015/09/25/4
- https://savannah.nongnu.org/bugs/?41309
