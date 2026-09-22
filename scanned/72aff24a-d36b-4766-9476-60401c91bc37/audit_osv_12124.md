# [H] CVE-2018-10392

## Summary
Severity: High
Advisory: CVE-2018-10392
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-26
Source: https://osv.dev/vulnerability/CVE-2018-10392
Type: osv

## Details
mapping0_forward in mapping0.c in Xiph.Org libvorbis 1.3.6 does not validate the number of channels, which allows remote attackers to cause a denial of service (heap-based buffer overflow or over-read) or possibly have unspecified other impact via a crafted file.

## References
- https://access.redhat.com/errata/RHSA-2019:3703
- https://lists.debian.org/debian-lts-announce/2019/11/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00023.html
- https://security.gentoo.org/glsa/202003-36
- https://gitlab.xiph.org/xiph/vorbis/issues/2335
