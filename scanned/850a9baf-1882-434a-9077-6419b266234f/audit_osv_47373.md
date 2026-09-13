# [H] CVE-2016-3981

## Summary
Severity: High
Advisory: CVE-2016-3981
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-3981
Type: osv

## Details
Heap-based buffer overflow in the bmp_read_rows function in pngxrbmp.c in OptiPNG before 0.7.6 allows remote attackers to cause a denial of service (out-of-bounds read or write access and crash) or possibly execute arbitrary code via a crafted image file.

## References
- https://security.gentoo.org/glsa/201608-01
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00061.html
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00065.html
- http://www.debian.org/security/2016/dsa-3546
- http://www.ubuntu.com/usn/USN-2951-1
- https://sourceforge.net/p/optipng/bugs/56/
- http://bugs.fi/media/afl/optipng/1/
