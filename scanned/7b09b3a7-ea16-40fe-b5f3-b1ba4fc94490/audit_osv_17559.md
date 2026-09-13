# [M] CVE-2020-16590

## Summary
Severity: Medium
Advisory: CVE-2020-16590
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16590
Type: osv

## Details
A double free vulnerability exists in the Binary File Descriptor (BFD) (aka libbrd) in GNU Binutils 2.35 in the process_symbol_table, as demonstrated in readelf, via a crafted file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=c98a4545dc7bf2bcaf1de539c4eb84784680eaa4
- https://security.netapp.com/advisory/ntap-20210115-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25821
