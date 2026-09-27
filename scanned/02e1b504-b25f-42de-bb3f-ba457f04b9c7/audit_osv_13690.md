# [M] CVE-2018-20822

## Summary
Severity: Medium
Advisory: CVE-2018-20822
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2018-20822
Type: osv

## Details
LibSass 3.5.4 allows attackers to cause a denial-of-service (uncontrolled recursion in Sass::Complex_Selector::perform in ast.hpp and Sass::Inspect::operator in inspect.cpp).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2671
