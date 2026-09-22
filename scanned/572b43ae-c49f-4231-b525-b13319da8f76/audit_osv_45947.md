# [M] JLSEC-2026-507

## Summary
Severity: Medium
Advisory: JLSEC-2026-507
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/JLSEC-2026-507
Type: osv

## Affected
- Julia: `libsass_jll` — affected >=0 <3.6.4+0

## Details
LibSass before 3.6.3 allows a NULL pointer dereference in Sass::Parser::parseCompoundSelector in `parser_selectors.cpp`.

## References
- https://github.com/sass/libsass/issues/3001
