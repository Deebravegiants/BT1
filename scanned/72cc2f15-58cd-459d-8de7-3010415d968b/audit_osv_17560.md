# [M] CVE-2020-16591

## Summary
Severity: Medium
Advisory: CVE-2020-16591
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16591
Type: osv

## Details
A Denial of Service vulnerability exists in the Binary File Descriptor (BFD) in GNU Binutils 2.35 due to an invalid read in process_symbol_table, as demonstrated in readeif.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=001890e1f9269697f7e0212430a51479271bdab2
- https://sourceware.org/bugzilla/show_bug.cgi?id=25822
- https://security.netapp.com/advisory/ntap-20210115-0003/
