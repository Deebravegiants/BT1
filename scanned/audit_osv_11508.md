# [C] CVE-2017-8287

## Summary
Severity: Critical
Advisory: CVE-2017-8287
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8287
Type: osv

## Details
FreeType 2 before 2017-03-26 has an out-of-bounds write caused by a heap-based buffer overflow related to the t1_builder_close_contour function in psaux/psobjs.c.

## References
- http://www.securityfocus.com/bid/99091
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.debian.org/security/2017/dsa-3839
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=941
- https://security.gentoo.org/glsa/201706-14
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/?id=3774fc08b502c3e685afca098b6e8a195aded6a0
