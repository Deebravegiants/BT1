# [M] CVE-2020-16592

## Summary
Severity: Medium
Advisory: CVE-2020-16592
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16592
Type: osv

## Details
A use after free issue exists in the Binary File Descriptor (BFD) library (aka libbfd) in GNU Binutils 2.34 in bfd_hash_lookup, as demonstrated in nm-new, that can cause a denial of service via a crafted file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DJIW6KKY2TSLD43XEZXG56WREIIBUIIQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UKIMSD5FIC3QFJDKNHR2PSO6JYJGCLHB/
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=7ecb51549ab1ec22aba5aaf34b70323cf0b8509a
- https://security.netapp.com/advisory/ntap-20210115-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25823
