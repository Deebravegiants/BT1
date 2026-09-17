# [M] CVE-2016-10061

## Summary
Severity: Medium
Advisory: CVE-2016-10061
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2016-10061
Type: osv

## Details
The ReadGROUP4Image function in coders/tiff.c in ImageMagick before 7.0.1-10 does not check the return value of the fputc function, which allows remote attackers to cause a denial of service (crash) via a crafted image file.

## References
- http://www.securityfocus.com/bid/95207
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1410471
- https://github.com/ImageMagick/ImageMagick/commit/4e914bbe371433f0590cefdf3bd5f3a5710069f9
- https://github.com/ImageMagick/ImageMagick/issues/196
