# [H] CVE-2018-19827

## Summary
Severity: High
Advisory: CVE-2018-19827
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19827
Type: osv

## Details
In LibSass 3.5.5, a use-after-free vulnerability exists in the SharedPtr class in SharedPtr.cpp (or SharedPtr.hpp) that may cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2782
