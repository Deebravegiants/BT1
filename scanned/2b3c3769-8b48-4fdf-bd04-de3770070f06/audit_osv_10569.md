# [H] CVE-2017-17124

## Summary
Severity: High
Advisory: CVE-2017-17124
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-04
Source: https://osv.dev/vulnerability/CVE-2017-17124
Type: osv

## Details
The _bfd_coff_read_string_table function in coffgen.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, does not properly validate the size of the external string table, which allows remote attackers to cause a denial of service (excessive memory consumption, or heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted COFF binary.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=b0029dce6867de1a2828293177b0e030d2f0f03c
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22507
