# [C] CVE-2017-18211

## Summary
Severity: Critical
Advisory: CVE-2017-18211
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-18211
Type: osv

## Details
In ImageMagick 7.0.7, a NULL pointer dereference vulnerability was found in the function saveBinaryCLProgram in magick/opencl.c because a program-lookup result is not checked, related to CacheOpenCLKernel.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- http://www.securityfocus.com/bid/103220
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/792
