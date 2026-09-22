# [M] CVE-2017-11505

## Summary
Severity: Medium
Advisory: CVE-2017-11505
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-21
Source: https://osv.dev/vulnerability/CVE-2017-11505
Type: osv

## Details
The ReadOneJNGImage function in coders/png.c in ImageMagick through 6.9.9-0 and 7.x through 7.0.6-1 allows remote attackers to cause a denial of service (large loop and CPU consumption) via a malformed JNG file.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867824
- https://github.com/ImageMagick/ImageMagick/issues/526
