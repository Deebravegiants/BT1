# [H] JLSEC-2026-1302

## Summary
Severity: High
Advisory: JLSEC-2026-1302
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1302
Type: osv

## Affected
- Julia: `Libcroco_jll` — affected unspecified

## Details
libcroco through 0.6.13 has excessive recursion in `cr_parser_parse_any_core` in cr-parser.c, leading to stack consumption.

## References
- http://www.openwall.com/lists/oss-security/2020/08/13/3
- http://www.openwall.com/lists/oss-security/2020/08/13/3
- http://www.openwall.com/lists/oss-security/2020/09/08/3
- http://www.openwall.com/lists/oss-security/2020/09/08/3
- https://gitlab.gnome.org/GNOME/libcroco/-/issues/8
- https://gitlab.gnome.org/GNOME/libcroco/-/issues/8
- https://security.gentoo.org/glsa/202208-33
- https://security.gentoo.org/glsa/202208-33
