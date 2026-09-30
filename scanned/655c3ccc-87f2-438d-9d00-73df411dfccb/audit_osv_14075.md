# [M] CVE-2018-6930

## Summary
Severity: Medium
Advisory: CVE-2018-6930
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-6930
Type: osv

## Details
A stack-based buffer over-read in the ComputeResizeImage function in the MagickCore/accelerate.c file of ImageMagick 7.0.7-22 allows a remote attacker to cause a denial of service (application crash) via a maliciously crafted pict file.

## References
- https://github.com/ImageMagick/ImageMagick/issues/967
