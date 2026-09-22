# [M] CVE-2018-14567

## Summary
Severity: Medium
Advisory: CVE-2018-14567
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-16
Source: https://osv.dev/vulnerability/CVE-2018-14567
Type: osv

## Details
libxml2 2.9.8, if --with-lzma is used, allows remote attackers to cause a denial of service (infinite loop) via a crafted XML file that triggers LZMA_MEMLIMIT_ERROR, as demonstrated by xmllint, a different vulnerability than CVE-2015-8035 and CVE-2018-9251.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00009.html
- http://www.securityfocus.com/bid/105198
- https://lists.debian.org/debian-lts-announce/2018/09/msg00035.html
- https://usn.ubuntu.com/3739-1/
- https://gitlab.gnome.org/GNOME/libxml2/commit/2240fbf5912054af025fb6e01e26375100275e74
