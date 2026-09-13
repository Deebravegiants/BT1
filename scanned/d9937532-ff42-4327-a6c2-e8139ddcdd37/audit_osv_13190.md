# [M] CVE-2018-18520

## Summary
Severity: Medium
Advisory: CVE-2018-18520
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-19
Source: https://osv.dev/vulnerability/CVE-2018-18520
Type: osv

## Details
An Invalid Memory Address Dereference exists in the function elf_end in libelf in elfutils through v0.174. Although eu-size is intended to support ar files inside ar files, handle_ar in size.c closes the outer ar file before handling all inner entries. The vulnerability allows attackers to cause a denial of service (application crash) with a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://access.redhat.com/errata/RHSA-2019:2197
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00030.html
- https://usn.ubuntu.com/4012-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23787
- https://sourceware.org/ml/elfutils-devel/2018-q4/msg00057.html
