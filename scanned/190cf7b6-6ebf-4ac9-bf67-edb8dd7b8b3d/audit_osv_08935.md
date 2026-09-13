# [M] CVE-2016-6905

## Summary
Severity: Medium
Advisory: CVE-2016-6905
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-6905
Type: osv

## Details
The read_image_tga function in gd_tga.c in the GD Graphics Library (aka libgd) before 2.2.3 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA image.

## References
- http://libgd.github.io/release-2.2.3.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00121.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00078.html
- http://www.openwall.com/lists/oss-security/2016/08/23/1
- http://www.securityfocus.com/bid/91743
- https://github.com/libgd/libgd/commit/01c61f8ab110a77ae64b5ca67c244c728c506f03
- https://github.com/libgd/libgd/commit/3c2b605d72e8b080dace1d98a6e50b46c1d12186
- https://github.com/libgd/libgd/issues/248
- https://github.com/libgd/libgd/pull/251
