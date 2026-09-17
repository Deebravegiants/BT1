# [M] CVE-2016-9298

## Summary
Severity: Medium
Advisory: CVE-2016-9298
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-9298
Type: osv

## Details
Heap overflow in the WaveletDenoiseImage function in MagickCore/fx.c in ImageMagick before 6.9.6-4 and 7.x before 7.0.3-6 allows remote attackers to cause a denial of service (crash) via a crafted image.

## References
- http://www.securityfocus.com/bid/94310
- https://security.gentoo.org/glsa/201702-09
- http://www.openwall.com/lists/oss-security/2016/11/13/1
- http://www.openwall.com/lists/oss-security/2016/11/14/10
- https://github.com/ImageMagick/ImageMagick/commit/3cbfb163cff9e5b8cdeace8312e9bfee810ed02b
- https://github.com/ImageMagick/ImageMagick/issues/296
