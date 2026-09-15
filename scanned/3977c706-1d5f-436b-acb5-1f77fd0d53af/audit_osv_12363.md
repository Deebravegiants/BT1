# [C] CVE-2018-11499

## Summary
Severity: Critical
Advisory: CVE-2018-11499
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-26
Source: https://osv.dev/vulnerability/CVE-2018-11499
Type: osv

## Details
A use-after-free vulnerability exists in handle_error() in sass_context.cpp in LibSass 3.4.x and 3.5.x through 3.5.4 that could be leveraged to cause a denial of service (application crash) or possibly unspecified other impact.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2643
