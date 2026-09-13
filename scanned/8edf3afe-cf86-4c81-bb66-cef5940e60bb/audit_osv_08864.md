# [H] CVE-2016-6491

## Summary
Severity: High
Advisory: CVE-2016-6491
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-6491
Type: osv

## Details
Buffer overflow in the Get8BIMProperty function in MagickCore/property.c in ImageMagick before 6.9.5-4 and 7.x before 7.0.2-6 allows remote attackers to cause a denial of service (out-of-bounds read, memory leak, and crash) via a crafted image.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/92186
- http://www.securitytracker.com/id/1036501
- https://github.com/ImageMagick/ImageMagick/blob/6.9.5-4/ChangeLog
- https://security.gentoo.org/glsa/201611-21
- http://www.openwall.com/lists/oss-security/2016/07/28/13
- https://github.com/ImageMagick/ImageMagick/commit/dd84447b63a71fa8c3f47071b09454efc667767b
- http://www.openwall.com/lists/oss-security/2016/07/28/15
