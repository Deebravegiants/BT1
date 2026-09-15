# [M] CVE-2020-28163

## Summary
Severity: Medium
Advisory: CVE-2020-28163
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2020-28163
Type: osv

## Details
libdwarf before 20201201 allows a dwarf_print_lines.c NULL pointer dereference and application crash via a DWARF5 line-table header that has an invalid FORM for a pathname.

## References
- http://web.archive.org/web/20190601140703/https://sourceforge.net/projects/libdwarf/
- https://www.prevanders.net/dwarfbug.html#DW202010-003
- https://bugzilla.redhat.com/show_bug.cgi?id=2026000
- https://github.com/davea42/libdwarf-code/commit/faf99408e3f9f706fc3809dd400e831f989778d3
