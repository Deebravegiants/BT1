# [M] CVE-2017-13132

## Summary
Severity: Medium
Advisory: CVE-2017-13132
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13132
Type: osv

## Details
In ImageMagick 7.0.6-8, the WritePDFImage function in coders/pdf.c operates on an incorrect data structure in the "dump uncompressed PseudoColor packets" step, which allows attackers to cause a denial of service (assertion failure in WriteBlobStream in MagickCore/blob.c) via a crafted file.

## References
- http://www.securityfocus.com/bid/100458
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/issues/674
