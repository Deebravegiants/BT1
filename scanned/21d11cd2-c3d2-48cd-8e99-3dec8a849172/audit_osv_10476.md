# [M] CVE-2017-15939

## Summary
Severity: Medium
Advisory: CVE-2017-15939
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15939
Type: osv

## Details
dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, mishandles NULL files in a .debug_line file table, which allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted ELF file, related to concat_filename. NOTE: this issue is caused by an incomplete fix for CVE-2017-15023.

## References
- http://www.securityfocus.com/bid/101613
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=a54018b72d75abf2e74bf36016702da06399c1d9
- https://security.gentoo.org/glsa/201801-01
- https://blogs.gentoo.org/ago/2017/10/24/binutils-null-pointer-dereference-in-concat_filename-dwarf2-c-incomplete-fix-for-cve-2017-15023/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22205
