# [H] CVE-2016-9275

## Summary
Severity: High
Advisory: CVE-2016-9275
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9275
Type: osv

## Details
Heap-based buffer overflow in the _dwarf_skim_forms function in libdwarf/dwarf_macro5.c in Libdwarf before 20161124 allows remote attackers to cause a denial of service (out-of-bounds read).

## References
- http://www.securityfocus.com/bid/94284
- http://www.openwall.com/lists/oss-security/2016/11/11/7
- https://blogs.gentoo.org/ago/2016/11/07/libdwarf-heap-based-buffer-overflow-in-_dwarf_skim_forms-dwarf_macro5-c
- https://bugzilla.redhat.com/show_bug.cgi?id=1394802
- https://sourceforge.net/p/libdwarf/code/ci/583f8834083b5ef834c497f5b47797e16101a9a6/
