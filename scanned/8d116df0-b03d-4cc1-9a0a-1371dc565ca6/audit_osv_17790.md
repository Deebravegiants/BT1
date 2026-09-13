# [M] CVE-2020-19724

## Summary
Severity: Medium
Advisory: CVE-2020-19724
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-19724
Type: osv

## Details
A memory consumption issue in get_data function in binutils/nm.c in GNU nm before 2.34 allows attackers to cause a denial of service via crafted command.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=805f38bc551de820bcd7b31d3c5731ae27cf853a
- https://sourceware.org/bugzilla/show_bug.cgi?id=25362
