# [M] CVE-2016-8679

## Summary
Severity: Medium
Advisory: CVE-2016-8679
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8679
Type: osv

## Details
The _dwarf_get_size_of_val function in libdwarf/dwarf_util.c in Libdwarf before 20161124 allows remote attackers to cause a denial of service (out-of-bounds read) by calling the dwarfdump command on a crafted file.

## References
- http://www.securityfocus.com/bid/93601
- http://www.openwall.com/lists/oss-security/2016/10/16/3
- https://blogs.gentoo.org/ago/2016/10/06/libdwarf-heap-based-buffer-overflow-in-_dwarf_get_size_of_val-dwarf_util-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1385689
