# [M] CVE-2017-11447

## Summary
Severity: Medium
Advisory: CVE-2017-11447
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11447
Type: osv

## Details
The ReadSCREENSHOTImage function in coders/screenshot.c in ImageMagick before 7.0.6-1 has memory leaks, causing denial of service.

## References
- http://www.securityfocus.com/bid/99948
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867897
- https://github.com/ImageMagick/ImageMagick/commit/72a50e400d98d7a2fd610caedfeb9af043dc5582
- https://github.com/ImageMagick/ImageMagick/issues/556
