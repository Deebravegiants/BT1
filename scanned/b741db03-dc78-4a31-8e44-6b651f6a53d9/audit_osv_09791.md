# [M] CVE-2017-11524

## Summary
Severity: Medium
Advisory: CVE-2017-11524
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11524
Type: osv

## Details
The WriteBlob function in MagickCore/blob.c in ImageMagick before 6.9.8-10 and 7.x before 7.6.0-0 allows remote attackers to cause a denial of service (assertion failure and application exit) via a crafted file.

## References
- http://www.securityfocus.com/bid/99934
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867798
- https://github.com/ImageMagick/ImageMagick/issues/506
