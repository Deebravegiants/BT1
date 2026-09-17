# [H] CVE-2018-11695

## Summary
Severity: High
Advisory: CVE-2018-11695
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2018-11695
Type: osv

## Details
An issue was discovered in LibSass <3.5.3. A NULL pointer dereference was found in the function Sass::Expand::operator which could be leveraged by an attacker to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://github.com/sass/libsass/issues/2664
- https://github.com/sass/libsass/pull/2631
- https://github.com/sass/libsass/releases
