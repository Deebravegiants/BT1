# [H] CVE-2019-15140

## Summary
Severity: High
Advisory: CVE-2019-15140
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15140
Type: osv

## Details
coders/mat.c in ImageMagick 7.0.8-43 Q16 allows remote attackers to cause a denial of service (use-after-free and application crash) or possibly have unspecified other impact by crafting a Matlab image file that is mishandled in ReadImage in MagickCore/constitute.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00028.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://www.debian.org/security/2020/dsa-4715
- https://github.com/ImageMagick/ImageMagick/commit/f7206618d27c2e69d977abf40e3035a33e5f6be0
- https://github.com/ImageMagick/ImageMagick/issues/1554
