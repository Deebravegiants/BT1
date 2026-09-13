# [M] CVE-2017-14503

## Summary
Severity: Medium
Advisory: CVE-2017-14503
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14503
Type: osv

## Details
libarchive 3.3.2 suffers from an out-of-bounds read within lha_read_data_none() in archive_read_support_format_lha.c when extracting a specially crafted lha archive, related to lha_crc16.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://usn.ubuntu.com/3736-1/
- https://access.redhat.com/errata/RHSA-2019:2298
- https://access.redhat.com/errata/RHSA-2019:3698
- https://github.com/libarchive/libarchive/issues/948
- https://security.gentoo.org/glsa/201908-11
- https://www.debian.org/security/2018/dsa-4360
- https://bugs.debian.org/875960
