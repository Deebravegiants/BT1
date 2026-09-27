# [M] CVE-2017-14684

## Summary
Severity: Medium
Advisory: CVE-2017-14684
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-22
Source: https://osv.dev/vulnerability/CVE-2017-14684
Type: osv

## Details
In ImageMagick 7.0.7-4 Q16, a memory leak vulnerability was found in the function ReadVIPSImage in coders/vips.c, which allows attackers to cause a denial of service (memory consumption in ResizeMagickMemory in MagickCore/memory.c) via a crafted file.

## References
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/770
