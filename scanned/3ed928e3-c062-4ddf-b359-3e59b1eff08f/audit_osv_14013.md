# [H] CVE-2018-6358

## Summary
Severity: High
Advisory: CVE-2018-6358
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-27
Source: https://osv.dev/vulnerability/CVE-2018-6358
Type: osv

## Details
The printDefineFont2 function (util/listfdb.c) in libming through 0.4.8 is vulnerable to a heap-based buffer overflow, which may allow attackers to cause a denial of service or unspecified other impact via a crafted FDB file.

## References
- https://github.com/libming/libming/issues/104
- https://lists.debian.org/debian-lts-announce/2018/04/msg00008.html
- https://security.gentoo.org/glsa/201904-24
