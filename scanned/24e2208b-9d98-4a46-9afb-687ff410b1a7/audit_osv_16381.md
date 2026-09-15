# [M] CVE-2019-6286

## Summary
Severity: Medium
Advisory: CVE-2019-6286
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-14
Source: https://osv.dev/vulnerability/CVE-2019-6286
Type: osv

## Details
In LibSass 3.5.5, a heap-based buffer over-read exists in Sass::Prelexer::skip_over_scopes in prelexer.hpp when called from Sass::Parser::parse_import(), a similar issue to CVE-2018-11693.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2815
