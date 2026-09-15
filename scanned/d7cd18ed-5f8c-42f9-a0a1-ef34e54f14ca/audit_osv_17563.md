# [M] CVE-2020-16599

## Summary
Severity: Medium
Advisory: CVE-2020-16599
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16599
Type: osv

## Details
A Null Pointer Dereference vulnerability exists in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.35, in _bfd_elf_get_symbol_version_string, as demonstrated in nm-new, that can cause a denial of service via a crafted file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=8d55d10ac0d112c586eaceb92e75bd9b80aadcc4
- https://security.netapp.com/advisory/ntap-20210122-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25842
