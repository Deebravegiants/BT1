# [H] CVE-2017-14103

## Summary
Severity: High
Advisory: CVE-2017-14103
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-01
Source: https://osv.dev/vulnerability/CVE-2017-14103
Type: osv

## Details
The ReadJNGImage and ReadOneJNGImage functions in coders/png.c in GraphicsMagick 1.3.26 do not properly manage image pointers after certain error conditions, which allows remote attackers to conduct use-after-free attacks via a crafted file, related to a ReadMNGImage out-of-order CloseBlob call. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-11403.

## References
- http://hg.code.sf.net/p/graphicsmagick/code/rev/98721124e51f
- https://blogs.gentoo.org/ago/2017/09/01/graphicsmagick-use-after-free-in-closeblob-blob-c-incomplete-fix-for-cve-2017-11403/
