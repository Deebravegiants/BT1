# [M] CVE-2016-7510

## Summary
Severity: Medium
Advisory: CVE-2016-7510
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-7510
Type: osv

## Details
The read_line_table_program function in dwarf_line_table_reader_common.c in libdwarf before 20160923 allows remote attackers to cause a denial of service (out-of-bounds read) via crafted input.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1377015
- https://sourceforge.net/p/libdwarf/bugs/4/
