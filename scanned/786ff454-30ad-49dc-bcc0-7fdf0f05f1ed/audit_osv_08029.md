# [M] CVE-2016-10060

## Summary
Severity: Medium
Advisory: CVE-2016-10060
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2016-10060
Type: osv

## Details
The ConcatenateImages function in MagickWand/magick-cli.c in ImageMagick before 7.0.1-10 does not check the return value of the fputc function, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/95208
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1410470
- https://github.com/ImageMagick/ImageMagick/commit/933e96f01a8c889c7bf5ffd30020e86a02a046e7
- https://github.com/ImageMagick/ImageMagick/issues/196
