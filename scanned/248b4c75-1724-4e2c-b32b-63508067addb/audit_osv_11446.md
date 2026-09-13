# [C] CVE-2017-7864

## Summary
Severity: Critical
Advisory: CVE-2017-7864
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7864
Type: osv

## Details
FreeType 2 before 2017-02-02 has an out-of-bounds write caused by a heap-based buffer overflow related to the tt_size_reset function in truetype/ttobjs.c.

## References
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/97673
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=509
- https://security.gentoo.org/glsa/201706-14
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/?id=e6699596af5c5d6f0ae0ea06e19df87dce088df8
