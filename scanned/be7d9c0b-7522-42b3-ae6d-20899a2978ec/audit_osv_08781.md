# [C] CVE-2016-5841

## Summary
Severity: Critical
Advisory: CVE-2016-5841
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-5841
Type: osv

## Details
Integer overflow in MagickCore/profile.c in ImageMagick before 7.0.2-1 allows remote attackers to cause a denial of service (segmentation fault) or possibly execute arbitrary code via vectors involving the offset variable.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91394
- https://github.com/ImageMagick/ImageMagick/commit/d8ab7f046587f2e9f734b687ba7e6e10147c294b
- http://www.openwall.com/lists/oss-security/2016/06/23/1
- http://www.openwall.com/lists/oss-security/2016/06/25/3
- https://github.com/ImageMagick/ImageMagick/commits/7.0.2-1
