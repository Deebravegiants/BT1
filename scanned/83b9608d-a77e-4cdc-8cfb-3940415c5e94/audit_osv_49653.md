# [M] CVE-2019-15144

## Summary
Severity: Medium
Advisory: CVE-2019-15144
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15144
Type: osv

## Details
In DjVuLibre 3.5.27, the sorting functionality (aka GArrayTemplate<TYPE>::sort) allows attackers to cause a denial-of-service (application crash due to an Uncontrolled Recursion) by crafting a PBM image file that is mishandled in libdjvu/GContainer.h.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FPMG3VY33XGMIKE6QDYIUVS6A7GNTHTK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JO65AWU7LEWNF6DDCZPRFTR2ZPP5XK6L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M7F7544WASYMOTFDR2WUEOQLN3ZEXNU4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QUEME45HVGTMDOYODAZYQOGWSZ2CEFWZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RYZTGKWY3NAKMIMTFYGN4ZO5XEQWPYRL/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00087.html
- https://security.gentoo.org/glsa/202007-36
- https://usn.ubuntu.com/4198-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00086.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00022.html
- https://www.debian.org/security/2021/dsa-5032
- https://sourceforge.net/p/djvu/djvulibre-git/ci/e15d51510048927f172f1bf1f27ede65907d940d/
- https://sourceforge.net/p/djvu/bugs/299/
