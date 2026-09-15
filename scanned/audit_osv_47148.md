# [C] CVE-2015-9290

## Summary
Severity: Critical
Advisory: CVE-2015-9290
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2015-9290
Type: osv

## Details
In FreeType before 2.6.1, a buffer over-read occurs in type1/t1parse.c on function T1_Get_Private_Dict where there is no check that the new values of cur and limit are sensible before going to Again.

## References
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/src/type1/t1parse.c?id=e3058617f384cb6709f3878f753fa17aca9e3a30
- https://savannah.nongnu.org/bugs/?45923
- https://savannah.nongnu.org/bugs/?45923
- http://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/src/type1/t1parse.c?id=e3058617f384cb6709f3878f753fa17aca9e3a30
- https://lists.debian.org/debian-lts-announce/2019/08/msg00019.html
- https://support.f5.com/csp/article/K38315305
- https://support.f5.com/csp/article/K38315305?utm_source=f5support&amp%3Butm_medium=RSS
