# [M] CVE-2016-5010

## Summary
Severity: Medium
Advisory: CVE-2016-5010
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-5010
Type: osv

## Details
coders/tiff.c in ImageMagick before 6.9.5-3 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TIFF file.

## References
- https://security.gentoo.org/glsa/201611-21
- http://git.imagemagick.org/repos/ImageMagick/commit/c20de102cc57f3739a8870f79e728e3b0bea18c0
- https://bugzilla.redhat.com/show_bug.cgi?id=1354500
