# [M] CVE-2017-12671

## Summary
Severity: Medium
Advisory: CVE-2017-12671
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12671
Type: osv

## Details
In ImageMagick 7.0.6-3, a missing NULL assignment was found in coders/png.c, leading to an invalid free in the function RelinquishMagickMemory in MagickCore/memory.c, which allows attackers to cause a denial of service.

## References
- https://www.debian.org/security/2017/dsa-4019
- https://github.com/ImageMagick/ImageMagick/issues/621
