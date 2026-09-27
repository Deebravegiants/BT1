# [H] CVE-2016-10252

## Summary
Severity: High
Advisory: CVE-2016-10252
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2016-10252
Type: osv

## Details
Memory leak in the IsOptionMember function in MagickCore/option.c in ImageMagick before 6.9.2-2, as used in ODR-PadEnc and other products, allows attackers to trigger memory consumption.

## References
- http://www.debian.org/security/2017/dsa-3808
- https://github.com/Opendigitalradio/ODR-PadEnc/issues/2
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=857426
- http://git.imagemagick.org/repos/ImageMagick/commit/6790815c75bdea0357df5564345847856e995d6b
