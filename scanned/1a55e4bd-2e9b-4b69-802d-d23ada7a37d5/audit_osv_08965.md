# [M] CVE-2016-7101

## Summary
Severity: Medium
Advisory: CVE-2016-7101
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-7101
Type: osv

## Details
The SGI coder in ImageMagick before 7.0.2-10 allows remote attackers to cause a denial of service (out-of-bounds read) via a large row value in an sgi file.

## References
- http://www.securityfocus.com/bid/93181
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=836776
- http://www.openwall.com/lists/oss-security/2016/09/26/8
- https://github.com/ImageMagick/ImageMagick/commit/7afcf9f71043df15508e46f079387bd4689a738d
- https://github.com/ImageMagick/ImageMagick/commit/8f8959033e4e59418d6506b345829af1f7a71127
