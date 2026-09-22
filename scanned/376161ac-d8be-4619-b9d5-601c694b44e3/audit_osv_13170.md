# [M] CVE-2018-18310

## Summary
Severity: Medium
Advisory: CVE-2018-18310
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/CVE-2018-18310
Type: osv

## Details
An invalid memory address dereference was discovered in dwfl_segment_report_module.c in libdwfl in elfutils through v0.174. The vulnerability allows attackers to cause a denial of service (application crash) with a crafted ELF file, as demonstrated by consider_notes.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://access.redhat.com/errata/RHSA-2019:2197
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00030.html
- https://usn.ubuntu.com/4012-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23752
- https://sourceware.org/ml/elfutils-devel/2018-q4/msg00022.html
