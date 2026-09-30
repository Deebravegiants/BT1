# [H] CVE-2015-9268

## Summary
Severity: High
Advisory: CVE-2015-9268
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-01
Source: https://osv.dev/vulnerability/CVE-2015-9268
Type: osv

## Details
Nullsoft Scriptable Install System (NSIS) before 2.49 has unsafe implicit linking against Version.dll. In other words, there is no protection mechanism in which a wrapper function resolves the dependency at an appropriate time during runtime.

## References
- http://jvn.jp/en/jp/JVN68418039/index.html
- https://lists.debian.org/debian-lts-announce/2018/11/msg00041.html
- https://sourceforge.net/p/nsis/bugs/1125/
- https://lists.debian.org/debian-lts-announce/2018/11/msg00041.html
- https://sourceforge.net/p/nsis/bugs/1125/
- https://sourceforge.net/p/nsis/bugs/1125/
- https://sourceforge.net/p/nsis/bugs/1125/
