# [M] CVE-2019-7664

## Summary
Severity: Medium
Advisory: CVE-2019-7664
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-09
Source: https://osv.dev/vulnerability/CVE-2019-7664
Type: osv

## Details
In elfutils 0.175, a negative-sized memcpy is attempted in elf_cvt_note in libelf/note_xlate.h because of an incorrect overflow check. Crafted elf input causes a segmentation fault, leading to denial of service (program crash).

## References
- https://access.redhat.com/errata/RHSA-2019:2197
- https://access.redhat.com/errata/RHSA-2019:3575
- https://sourceware.org/bugzilla/show_bug.cgi?id=24084
