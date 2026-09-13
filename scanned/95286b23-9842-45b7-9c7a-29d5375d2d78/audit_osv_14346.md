# [M] CVE-2018-9251

## Summary
Severity: Medium
Advisory: CVE-2018-9251
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9251
Type: osv

## Details
The xz_decomp function in xzlib.c in libxml2 2.9.8, if --with-lzma is used, allows remote attackers to cause a denial of service (infinite loop) via a crafted XML file that triggers LZMA_MEMLIMIT_ERROR, as demonstrated by xmllint, a different vulnerability than CVE-2015-8035.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00035.html
- https://bugzilla.gnome.org/show_bug.cgi?id=794914
