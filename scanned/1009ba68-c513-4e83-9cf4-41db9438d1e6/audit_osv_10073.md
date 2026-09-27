# [M] CVE-2017-13061

## Summary
Severity: Medium
Advisory: CVE-2017-13061
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-22
Source: https://osv.dev/vulnerability/CVE-2017-13061
Type: osv

## Details
In ImageMagick 7.0.6-5, a length-validation vulnerability was found in the function ReadPSDLayersInternal in coders/psd.c, which allows attackers to cause a denial of service (ReadPSDImage memory exhaustion) via a crafted file.

## References
- http://www.securityfocus.com/bid/100481
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/645
- https://security.gentoo.org/glsa/201711-07
