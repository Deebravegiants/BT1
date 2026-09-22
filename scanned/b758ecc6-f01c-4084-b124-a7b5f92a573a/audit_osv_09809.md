# [H] CVE-2017-11554

## Summary
Severity: High
Advisory: CVE-2017-11554
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11554
Type: osv

## Details
There is a stack consumption vulnerability in the lex function in parser.hpp (as used in sassc) in LibSass 3.4.5. A crafted input will lead to a remote denial of service.

## References
- https://github.com/sass/libsass/issues/2445
- https://bugzilla.redhat.com/show_bug.cgi?id=1471780
