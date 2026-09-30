# [H] CVE-2017-16826

## Summary
Severity: High
Advisory: CVE-2017-16826
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16826
Type: osv

## Details
The coff_slurp_line_table function in coffcode.h in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, allows remote attackers to cause a denial of service (invalid memory access and application crash) or possibly have unspecified other impact via a crafted PE file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=a67d66eb97e7613a38ffe6622d837303b3ecd31d
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22376
