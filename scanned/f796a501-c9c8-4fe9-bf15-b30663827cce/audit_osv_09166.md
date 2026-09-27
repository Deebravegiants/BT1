# [M] CVE-2016-8678

## Summary
Severity: Medium
Advisory: CVE-2016-8678
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8678
Type: osv

## Details
The IsPixelMonochrome function in MagickCore/pixel-accessor.h in ImageMagick 7.0.3.0 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted file.  NOTE: the vendor says "This is a Q64 issue and we do not support Q64."

## References
- http://www.openwall.com/lists/oss-security/2016/10/16/2
- http://www.openwall.com/lists/oss-security/2016/12/08/18
- http://www.securityfocus.com/bid/93599
- https://bugzilla.redhat.com/show_bug.cgi?id=1385694
- https://github.com/ImageMagick/ImageMagick/issues/272
