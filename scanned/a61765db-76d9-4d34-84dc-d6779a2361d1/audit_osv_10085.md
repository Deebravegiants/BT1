# [H] CVE-2017-13143

## Summary
Severity: High
Advisory: CVE-2017-13143
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13143
Type: osv

## Details
In ImageMagick before 6.9.7-6 and 7.x before 7.0.4-6, the ReadMATImage function in coders/mat.c uses uninitialized data, which might allow remote attackers to obtain sensitive information from process memory.

## References
- https://usn.ubuntu.com/3681-1/
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4019
- https://www.debian.org/security/2018/dsa-4204
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870012
- https://github.com/ImageMagick/ImageMagick/commit/51b0ae01709adc1e4a9245e158ef17b85a110960
- https://github.com/ImageMagick/ImageMagick/issues/362
