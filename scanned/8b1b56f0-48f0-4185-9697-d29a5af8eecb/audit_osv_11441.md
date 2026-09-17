# [C] CVE-2017-7858

## Summary
Severity: Critical
Advisory: CVE-2017-7858
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7858
Type: osv

## Details
FreeType 2 before 2017-03-07 has an out-of-bounds write related to the TT_Get_MM_Var function in truetype/ttgxvar.c and the sfnt_init_face function in sfnt/sfobjs.c.

## References
- http://www.securityfocus.com/bid/97682
- https://security.gentoo.org/glsa/201706-14
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=738
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/?id=779309744222a736eba0f1731e8162fce6288d4e
