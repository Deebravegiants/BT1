# [M] CVE-2017-9141

## Summary
Severity: Medium
Advisory: CVE-2017-9141
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-9141
Type: osv

## Details
In ImageMagick 7.0.5-7 Q16, a crafted file could trigger an assertion failure in the ResetImageProfileIterator function in MagickCore/profile.c because of missing checks in the ReadDDSImage function in coders/dds.c.

## References
- http://www.debian.org/security/2017/dsa-3863
- http://www.securityfocus.com/bid/98606
- https://github.com/ImageMagick/ImageMagick/commit/0c5b1e430a83ef793a7334bbbee408cf3c628699
- https://github.com/ImageMagick/ImageMagick/issues/489
