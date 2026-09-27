# [M] CVE-2017-9865

## Summary
Severity: Medium
Advisory: CVE-2017-9865
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2017-9865
Type: osv

## Details
The function GfxImageColorMap::getGray in GfxState.cc in Poppler 0.54.0 allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) via a crafted PDF document, related to missing color-map validation in ImageOutputDev.cc.

## References
- https://usn.ubuntu.com/4042-1/
- https://www.debian.org/security/2018/dsa-4079
- http://somevulnsofadlab.blogspot.com/2017/06/popplerstack-buffer-overflow-in.html
- https://security.gentoo.org/glsa/201801-17
- https://bugs.freedesktop.org/show_bug.cgi?id=100774
