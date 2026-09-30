# [H] CVE-2017-16827

## Summary
Severity: High
Advisory: CVE-2017-16827
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16827
Type: osv

## Details
The aout_get_external_symbols function in aoutx.h in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, allows remote attackers to cause a denial of service (slurp_symtab invalid free and application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=0301ce1486b1450f219202677f30d0fa97335419
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22306
