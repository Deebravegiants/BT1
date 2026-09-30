# [C] CVE-2017-9117

## Summary
Severity: Critical
Advisory: CVE-2017-9117
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-21
Source: https://osv.dev/vulnerability/CVE-2017-9117
Type: osv

## Details
In LibTIFF 4.0.6 and possibly other versions, the program processes BMP images without verifying that biWidth and biHeight in the bitmap-information header match the actual input, as demonstrated by a heap-based buffer over-read in bmp2tiff. NOTE: mentioning bmp2tiff does not imply that the activation point is in the bmp2tiff.c file (which was removed before the 4.0.7 release).

## References
- http://www.securityfocus.com/bid/98581
- https://usn.ubuntu.com/3606-1/
- http://bugzilla.maptools.org/show_bug.cgi?id=2690
- https://gitlab.com/libtiff/libtiff/-/issues/89
