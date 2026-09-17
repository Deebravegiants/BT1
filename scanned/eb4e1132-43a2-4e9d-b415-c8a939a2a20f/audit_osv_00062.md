# [H] ALPINE-CVE-2016-10244

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-10244
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10244
Type: osv

## Affected
- Alpine:v3.2: `freetype` — affected >=0 <2.5.5-r1
- Alpine:v3.3: `freetype` — affected >=0 <2.6.3-r0
- Alpine:v3.4: `freetype` — affected >=0 <2.6.3-r1

## Details
The parse_charstrings function in type1/t1load.c in FreeType 2 before 2.7 does not ensure that a font contains a glyph name, which allows remote attackers to cause a denial of service (heap-based buffer over-read) or possibly have unspecified other impact via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10244
