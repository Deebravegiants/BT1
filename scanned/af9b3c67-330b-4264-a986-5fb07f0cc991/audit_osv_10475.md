# [H] CVE-2017-15938

## Summary
Severity: High
Advisory: CVE-2017-15938
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15938
Type: osv

## Details
dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, miscalculates DW_FORM_ref_addr die refs in the case of a relocatable object file, which allows remote attackers to cause a denial of service (find_abstract_instance_name invalid memory read, segmentation fault, and application crash).

## References
- http://www.securityfocus.com/bid/101610
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=1b86808a86077722ee4f42ff97f836b12420bb2a
- https://security.gentoo.org/glsa/201801-01
- https://blogs.gentoo.org/ago/2017/10/24/binutils-invalid-memory-read-in-find_abstract_instance_name-dwarf2-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22209
