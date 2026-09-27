# [M] CVE-2019-7665

## Summary
Severity: Medium
Advisory: CVE-2019-7665
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-09
Source: https://osv.dev/vulnerability/CVE-2019-7665
Type: osv

## Details
In elfutils 0.175, a heap-based buffer over-read was discovered in the function elf32_xlatetom in elf32_xlatetom.c in libelf. A crafted ELF input can cause a segmentation fault leading to denial of service (program crash) because ebl_core_note does not reject malformed core file notes.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://access.redhat.com/errata/RHSA-2019:2197
- https://access.redhat.com/errata/RHSA-2019:3575
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00030.html
- https://usn.ubuntu.com/4012-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24089
- https://sourceware.org/ml/elfutils-devel/2019-q1/msg00049.html
