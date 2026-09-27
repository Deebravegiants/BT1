# [M] CVE-2019-15143

## Summary
Severity: Medium
Advisory: CVE-2019-15143
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15143
Type: osv

## Details
In DjVuLibre 3.5.27, the bitmap reader component allows attackers to cause a denial-of-service error (resource exhaustion caused by a GBitmap::read_rle_raw infinite loop) by crafting a corrupted image file, related to libdjvu/DjVmDir.cpp and libdjvu/GBitmap.cpp.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FPMG3VY33XGMIKE6QDYIUVS6A7GNTHTK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JO65AWU7LEWNF6DDCZPRFTR2ZPP5XK6L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M7F7544WASYMOTFDR2WUEOQLN3ZEXNU4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QUEME45HVGTMDOYODAZYQOGWSZ2CEFWZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RYZTGKWY3NAKMIMTFYGN4ZO5XEQWPYRL/
- https://usn.ubuntu.com/4198-1/
- https://www.debian.org/security/2021/dsa-5032
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00086.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00036.html
- https://sourceforge.net/p/djvu/djvulibre-git/ci/b1f4e1b2187d9e5010cd01ceccf20b4a11ce723f/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00087.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00022.html
- https://security.gentoo.org/glsa/202007-36
- https://sourceforge.net/p/djvu/bugs/297/
