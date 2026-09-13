# [M] CVE-2017-14633

## Summary
Severity: Medium
Advisory: CVE-2017-14633
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14633
Type: osv

## Details
In Xiph.Org libvorbis 1.3.5, an out-of-bounds array read vulnerability exists in the function mapping0_forward() in mapping0.c, which may lead to DoS when operating on a crafted audio file with vorbis_analysis().

## References
- https://gitlab.xiph.org/xiph/vorbis/issues/2329
- https://lists.debian.org/debian-lts-announce/2018/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00021.html
- https://usn.ubuntu.com/3569-1/
- https://www.debian.org/security/2018/dsa-4113
