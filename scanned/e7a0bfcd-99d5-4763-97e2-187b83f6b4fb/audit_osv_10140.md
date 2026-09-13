# [H] CVE-2017-14041

## Summary
Severity: High
Advisory: CVE-2017-14041
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-14041
Type: osv

## Details
A stack-based buffer overflow was discovered in the pgxtoimage function in bin/jp2/convert.c in OpenJPEG 2.2.0. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service or possibly remote code execution.

## References
- http://www.debian.org/security/2017/dsa-4013
- http://www.securityfocus.com/bid/100555
- https://blogs.gentoo.org/ago/2017/08/28/openjpeg-stack-based-buffer-overflow-write-in-pgxtoimage-convert-c/
- https://github.com/uclouvain/openjpeg/commit/e5285319229a5d77bf316bb0d3a6cbd3cb8666d9
- https://github.com/uclouvain/openjpeg/issues/997
