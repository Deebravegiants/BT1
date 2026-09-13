# [M] CVE-2020-27756

## Summary
Severity: Medium
Advisory: CVE-2020-27756
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-27756
Type: osv

## Details
In ParseMetaGeometry() of MagickCore/geometry.c, image height and width calculations can lead to divide-by-zero conditions which also lead to undefined behavior. This flaw can be triggered by a crafted input file processed by ImageMagick and could impact application availability. The patch uses multiplication in addition to the function `PerceptibleReciprocal()` in order to prevent such divide-by-zero conditions. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1894233
