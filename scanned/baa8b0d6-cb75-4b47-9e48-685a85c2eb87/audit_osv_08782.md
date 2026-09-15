# [H] CVE-2016-5842

## Summary
Severity: High
Advisory: CVE-2016-5842
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-5842
Type: osv

## Details
MagickCore/property.c in ImageMagick before 7.0.2-1 allows remote attackers to obtain sensitive memory information via vectors involving the q variable, which triggers an out-of-bounds read.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- https://security.gentoo.org/glsa/201611-21
- http://www.openwall.com/lists/oss-security/2016/06/23/1
- https://github.com/ImageMagick/ImageMagick/commit/d8ab7f046587f2e9f734b687ba7e6e10147c294b
- https://github.com/ImageMagick/ImageMagick/commits/7.0.2-1
- http://www.openwall.com/lists/oss-security/2016/06/25/3
- http://www.securityfocus.com/bid/91394
