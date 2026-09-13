# [C] CVE-2017-7857

## Summary
Severity: Critical
Advisory: CVE-2017-7857
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7857
Type: osv

## Details
FreeType 2 before 2017-03-08 has an out-of-bounds write caused by a heap-based buffer overflow related to the TT_Get_MM_Var function in truetype/ttgxvar.c and the sfnt_init_face function in sfnt/sfobjs.c.

## References
- http://www.securityfocus.com/bid/97680
- https://security.gentoo.org/glsa/201706-14
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=759
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/?id=7bbb91fbf47fc0775cc9705673caf0c47a81f94b
