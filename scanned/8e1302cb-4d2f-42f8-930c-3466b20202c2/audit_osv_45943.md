# [M] JLSEC-2026-501

## Summary
Severity: Medium
Advisory: JLSEC-2026-501
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/JLSEC-2026-501
Type: osv

## Affected
- Julia: `libsass_jll` — affected >=0 <3.6.4+0

## Details
In LibSass 3.5.5, a NULL Pointer Dereference in the function `Sass::Selector_List::populate_extends` in SharedPtr.hpp (used by ast.cpp and `ast_selectors.cpp`) may cause a Denial of Service (application crash) via a crafted sass input file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2779
