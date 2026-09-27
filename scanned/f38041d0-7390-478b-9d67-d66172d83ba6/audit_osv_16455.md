# [M] CVE-2019-7149

## Summary
Severity: Medium
Advisory: CVE-2019-7149
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-7149
Type: osv

## Details
A heap-based buffer over-read was discovered in the function read_srclines in dwarf_getsrclines.c in libdw in elfutils 0.175. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by eu-nm.

## References
- https://usn.ubuntu.com/4012-1/
- https://access.redhat.com/errata/RHSA-2019:2197
- https://access.redhat.com/errata/RHSA-2019:3575
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=24102
- https://sourceware.org/ml/elfutils-devel/2019-q1/msg00068.html
