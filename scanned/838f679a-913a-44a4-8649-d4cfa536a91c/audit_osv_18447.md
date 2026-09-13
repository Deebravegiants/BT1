# [M] CVE-2020-27760

## Summary
Severity: Medium
Advisory: CVE-2020-27760
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-27760
Type: osv

## Details
In `GammaImage()` of /MagickCore/enhance.c, depending on the `gamma` value, it's possible to trigger a divide-by-zero condition when a crafted input file is processed by ImageMagick. This could lead to an impact to application availability. The patch uses the `PerceptibleReciprocal()` to prevent the divide-by-zero from occurring. This flaw affects ImageMagick versions prior to ImageMagick 7.0.8-68.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1894239
