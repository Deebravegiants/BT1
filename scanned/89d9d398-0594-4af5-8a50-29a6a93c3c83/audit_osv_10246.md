# [M] CVE-2017-14529

## Summary
Severity: Medium
Advisory: CVE-2017-14529
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-18
Source: https://osv.dev/vulnerability/CVE-2017-14529
Type: osv

## Details
The pe_print_idata function in peXXigen.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, mishandles HintName vector entries, which allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted PE file, related to the bfd_getl16 function.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=4d465c689a8fb27212ef358d0aee89d60dee69a6
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=dcaaca89e8618eba35193c27afcb1cfa54f74582
- https://sourceware.org/bugzilla/show_bug.cgi?id=22113
