# [M] CVE-2018-7443

## Summary
Severity: Medium
Advisory: CVE-2018-7443
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7443
Type: osv

## Details
The ReadTIFFImage function in coders/tiff.c in ImageMagick 7.0.7-23 Q16 does not properly validate the amount of image data in a file, which allows remote attackers to cause a denial of service (memory allocation failure in the AcquireMagickMemory function in MagickCore/memory.c).

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/02/msg00028.html
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/999
