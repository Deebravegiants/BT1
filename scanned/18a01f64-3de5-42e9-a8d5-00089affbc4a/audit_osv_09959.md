# [H] CVE-2017-12448

## Summary
Severity: High
Advisory: CVE-2017-12448
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12448
Type: osv

## Details
The bfd_cache_close function in bfd/cache.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29 and earlier, allows remote attackers to cause a heap use after free and possibly achieve code execution via a crafted nested archive file. This issue occurs because incorrect functions are called during an attempt to release memory. The issue can be addressed by better input validation in the bfd_generic_archive_p function in bfd/archive.c.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=21787
