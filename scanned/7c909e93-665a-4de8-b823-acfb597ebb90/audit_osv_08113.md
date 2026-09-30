# [C] CVE-2016-10328

## Summary
Severity: Critical
Advisory: CVE-2016-10328
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-10328
Type: osv

## Details
FreeType 2 before 2016-12-16 has an out-of-bounds write caused by a heap-based buffer overflow related to the cff_parser_run function in cff/cffparse.c.

## References
- http://savannah.nongnu.org/bugs/?func=detailitem&item_id=49858
- http://www.securityfocus.com/bid/97677
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=289
- https://security.gentoo.org/glsa/201706-14
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/?id=beecf80a6deecbaf5d264d4f864451bde4fe98b8
