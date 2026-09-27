# [C] CVE-2019-17544

## Summary
Severity: Critical
Advisory: CVE-2019-17544
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/CVE-2019-17544
Type: osv

## Details
libaspell.a in GNU Aspell before 0.60.8 has a stack-based buffer over-read in acommon::unescape in common/getdata.cpp via an isolated \ character.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2021/07/msg00021.html
- https://usn.ubuntu.com/4155-2/
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=16109
- https://github.com/GNUAspell/aspell/compare/rel-0.60.7...rel-0.60.8
- https://usn.ubuntu.com/4155-1/
- https://www.debian.org/security/2021/dsa-4948
- https://github.com/GNUAspell/aspell/commit/80fa26c74279fced8d778351cff19d1d8f44fe4e
