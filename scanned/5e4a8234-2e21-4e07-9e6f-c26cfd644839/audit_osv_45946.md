# [M] JLSEC-2026-504

## Summary
Severity: Medium
Advisory: JLSEC-2026-504
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/JLSEC-2026-504
Type: osv

## Affected
- Julia: `libsass_jll` — affected >=0 <3.6.4+0

## Details
The parsing component in LibSass through 3.5.5 allows attackers to cause a denial-of-service (uncontrolled recursion in `Sass::Parser::parse_css_variable_value` in parser.cpp).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2658
