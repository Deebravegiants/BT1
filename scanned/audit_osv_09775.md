# [H] CVE-2017-11449

## Summary
Severity: High
Advisory: CVE-2017-11449
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11449
Type: osv

## Details
coders/mpc.c in ImageMagick before 7.0.6-1 does not enable seekable streams and thus cannot validate blob sizes, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via an image received from stdin.

## References
- http://www.securityfocus.com/bid/99958
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867896
- https://github.com/ImageMagick/ImageMagick/commit/529ff26b68febb2ac03062c58452ea0b4c6edbc1
- https://github.com/ImageMagick/ImageMagick/commit/b007dd3a048097d8f58949297f5b434612e1e1a3
- https://github.com/ImageMagick/ImageMagick/issues/556
