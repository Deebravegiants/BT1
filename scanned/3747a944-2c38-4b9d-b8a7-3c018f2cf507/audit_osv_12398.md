# [H] CVE-2018-11696

## Summary
Severity: High
Advisory: CVE-2018-11696
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2018-11696
Type: osv

## Details
An issue was discovered in LibSass through 3.5.4. A NULL pointer dereference was found in the function Sass::Inspect::operator which could be leveraged by an attacker to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://github.com/sass/libsass/issues/2665
