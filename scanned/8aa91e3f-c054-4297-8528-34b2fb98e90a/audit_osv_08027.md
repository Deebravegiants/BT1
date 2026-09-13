# [M] CVE-2016-10058

## Summary
Severity: Medium
Advisory: CVE-2016-10058
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-10058
Type: osv

## Details
Memory leak in the ReadPSDLayers function in coders/psd.c in ImageMagick before 6.9.6-3 allows remote attackers to cause a denial of service (memory consumption) via a crafted image file.

## References
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- http://www.securityfocus.com/bid/95212
- https://bugzilla.redhat.com/show_bug.cgi?id=1410467
- https://github.com/ImageMagick/ImageMagick/commit/47e8e6ceef979327614d0b8f0c76c6ecb18e09cf
- https://github.com/ImageMagick/ImageMagick/commit/4ec444f4eab88cf4bec664fafcf9cab50bc5ff6a
