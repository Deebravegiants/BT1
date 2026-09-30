# [H] CVE-2017-18209

## Summary
Severity: High
Advisory: CVE-2017-18209
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-18209
Type: osv

## Details
In the GetOpenCLCachedFilesDirectory function in magick/opencl.c in ImageMagick 7.0.7, a NULL pointer dereference vulnerability occurs because a memory allocation result is not checked, related to GetOpenCLCacheDirectory.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- http://www.securityfocus.com/bid/103218
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/790
