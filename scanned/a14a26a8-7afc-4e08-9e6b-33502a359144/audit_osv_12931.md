# [C] CVE-2018-16402

## Summary
Severity: Critical
Advisory: CVE-2018-16402
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16402
Type: osv

## Details
libelf/elf_end.c in elfutils 0.173 allows remote attackers to cause a denial of service (double free and application crash) or possibly have unspecified other impact because it tries to decompress twice.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://access.redhat.com/errata/RHSA-2019:2197
- https://lists.debian.org/debian-lts-announce/2021/10/msg00030.html
- https://usn.ubuntu.com/4012-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23528
