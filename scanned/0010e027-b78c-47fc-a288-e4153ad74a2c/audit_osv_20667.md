# [M] CVE-2021-3596

## Summary
Severity: Medium
Advisory: CVE-2021-3596
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-3596
Type: osv

## Details
A NULL pointer dereference flaw was found in ImageMagick in versions prior to 7.0.10-31 in ReadSVGImage() in coders/svg.c. This issue is due to not checking the return value from libxml2's xmlCreatePushParserCtxt() and uses the value directly, which leads to a crash and segmentation fault.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2022/05/msg00018.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1970569
- https://github.com/ImageMagick/ImageMagick/issues/2624
