# [M] CVE-2017-13133

## Summary
Severity: Medium
Advisory: CVE-2017-13133
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13133
Type: osv

## Details
In ImageMagick 7.0.6-8, the load_level function in coders/xcf.c lacks offset validation, which allows attackers to cause a denial of service (load_tile memory exhaustion) via a crafted file.

## References
- http://www.securityfocus.com/bid/100479
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/issues/679
