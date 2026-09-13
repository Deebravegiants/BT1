# [M] CVE-2016-6906

## Summary
Severity: Medium
Advisory: CVE-2016-6906
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-6906
Type: osv

## Details
The read_image_tga function in gd_tga.c in the GD Graphics Library (aka libgd) before 2.2.4 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file, related to the decompression buffer.

## References
- http://www.debian.org/security/2017/dsa-3777
- http://www.securityfocus.com/bid/96503
- https://github.com/libgd/libgd/blob/gd-2.2.4/CHANGELOG.md
- https://github.com/libgd/libgd/commit/58b6dde319c301b0eae27d12e2a659e067d80558
- https://github.com/libgd/libgd/commit/fb0e0cce0b9f25389ab56604c3547351617e1415
