# [M] CVE-2016-10046

## Summary
Severity: Medium
Advisory: CVE-2016-10046
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-10046
Type: osv

## Details
Heap-based buffer overflow in the DrawImage function in magick/draw.c in ImageMagick before 6.9.5-5 allows remote attackers to cause a denial of service (application crash) via a crafted image file.

## References
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- http://www.securityfocus.com/bid/95183
- https://bugzilla.redhat.com/show_bug.cgi?id=1410448
- https://github.com/ImageMagick/ImageMagick/commit/989f9f88ea6db09b99d25586e912c921c0da8d3f
