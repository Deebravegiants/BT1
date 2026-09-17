# [M] CVE-2017-17682

## Summary
Severity: Medium
Advisory: CVE-2017-17682
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17682
Type: osv

## Details
In ImageMagick 7.0.7-12 Q16, a large loop vulnerability was found in the function ExtractPostscript in coders/wpg.c, which allows attackers to cause a denial of service (CPU exhaustion) via a crafted wpg image file that triggers a ReadWPGImage call.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/3681-1/
- http://www.securityfocus.com/bid/102202
- https://lists.debian.org/debian-lts-announce/2018/01/msg00000.html
- https://github.com/ImageMagick/ImageMagick/issues/870
