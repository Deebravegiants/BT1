# [M] CVE-2017-18250

## Summary
Severity: Medium
Advisory: CVE-2017-18250
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2017-18250
Type: osv

## Details
An issue was discovered in ImageMagick 7.0.7. A NULL pointer dereference vulnerability was found in the function LogOpenCLBuildFailure in MagickCore/opencl.c, which allows attackers to cause a denial of service via a crafted file.

## References
- https://github.com/ImageMagick/ImageMagick/issues/793
