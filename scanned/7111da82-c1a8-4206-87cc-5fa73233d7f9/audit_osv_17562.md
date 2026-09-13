# [M] CVE-2020-16593

## Summary
Severity: Medium
Advisory: CVE-2020-16593
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16593
Type: osv

## Details
A Null Pointer Dereference vulnerability exists in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.35, in scan_unit_for_symbols, as demonstrated in addr2line, that can cause a denial of service via a crafted file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=aec72fda3b320c36eb99fc1c4cf95b10fc026729
- https://security.netapp.com/advisory/ntap-20210122-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25827
