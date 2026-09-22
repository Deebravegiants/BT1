# [M] CVE-2017-17123

## Summary
Severity: Medium
Advisory: CVE-2017-17123
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-04
Source: https://osv.dev/vulnerability/CVE-2017-17123
Type: osv

## Details
The coff_slurp_reloc_table function in coffcode.h in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted COFF based file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=4581a1c7d304ce14e714b27522ebf3d0188d6543
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22509
