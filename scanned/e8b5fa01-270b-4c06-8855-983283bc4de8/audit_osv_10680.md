# [C] CVE-2017-18210

## Summary
Severity: Critical
Advisory: CVE-2017-18210
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-18210
Type: osv

## Details
In ImageMagick 7.0.7, a NULL pointer dereference vulnerability was found in the function BenchmarkOpenCLDevices in MagickCore/opencl.c because a memory allocation result is not checked.

## References
- http://www.securityfocus.com/bid/103212
- https://github.com/ImageMagick/ImageMagick/issues/791
