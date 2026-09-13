# [H] CVE-2016-3982

## Summary
Severity: High
Advisory: CVE-2016-3982
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-3982
Type: osv

## Details
Off-by-one error in the bmp_rle4_fread function in pngxrbmp.c in OptiPNG before 0.7.6 allows remote attackers to cause a denial of service (out-of-bounds read or write access and crash) or possibly execute arbitrary code via a crafted image file, which triggers a heap-based buffer overflow.

## References
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00061.html
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00065.html
- http://www.debian.org/security/2016/dsa-3546
- http://www.ubuntu.com/usn/USN-2951-1
- https://security.gentoo.org/glsa/201608-01
- http://bugs.fi/media/afl/optipng/2/
- https://sourceforge.net/p/optipng/bugs/57/
