# [M] CVE-2018-19797

## Summary
Severity: Medium
Advisory: CVE-2018-19797
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19797
Type: osv

## Details
In LibSass 3.5.5, a NULL Pointer Dereference in the function Sass::Selector_List::populate_extends in SharedPtr.hpp (used by ast.cpp and ast_selectors.cpp) may cause a Denial of Service (application crash) via a crafted sass input file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2779
