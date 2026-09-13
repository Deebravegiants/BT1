# [H] CVE-2017-6497

## Summary
Severity: High
Advisory: CVE-2017-6497
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/CVE-2017-6497
Type: osv

## Details
An issue was discovered in ImageMagick 6.9.7. A specially crafted psd file could lead to a NULL pointer dereference (thus, a DoS).

## References
- http://www.securityfocus.com/bid/96594
- https://bugs.debian.org/856882
- https://github.com/ImageMagick/ImageMagick/commit/7f2dc7a1afc067d0c89f12c82bcdec0445fb1b94
