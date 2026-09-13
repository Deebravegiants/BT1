# [H] CVE-2017-15281

## Summary
Severity: High
Advisory: CVE-2017-15281
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-12
Source: https://osv.dev/vulnerability/CVE-2017-15281
Type: osv

## Details
ReadPSDImage in coders/psd.c in ImageMagick 7.0.7-6 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted file, related to "Conditional jump or move depends on uninitialised value(s)."

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- http://www.securityfocus.com/bid/101276
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/832
