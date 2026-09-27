# [M] CVE-2018-7570

## Summary
Severity: Medium
Advisory: CVE-2018-7570
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-28
Source: https://osv.dev/vulnerability/CVE-2018-7570
Type: osv

## Details
The assign_file_positions_for_non_load_sections function in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via an ELF file with a RELRO segment that lacks a matching LOAD segment, as demonstrated by objcopy.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=01f7e10cf2dcf403462b2feed06c43135651556d
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22881
