# [M] CVE-2017-11526

## Summary
Severity: Medium
Advisory: CVE-2017-11526
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11526
Type: osv

## Details
The ReadOneMNGImage function in coders/png.c in ImageMagick before 6.9.9-0 and 7.x before 7.0.6-1 allows remote attackers to cause a denial of service (large loop and CPU consumption) via a crafted file.

## References
- http://www.securityfocus.com/bid/99932
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867825
- https://github.com/ImageMagick/ImageMagick/issues/527
