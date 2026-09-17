# [M] CVE-2016-8680

## Summary
Severity: Medium
Advisory: CVE-2016-8680
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8680
Type: osv

## Details
The _dwarf_get_abbrev_for_code function in dwarf_util.c in libdwarf 20161001 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) by calling the dwarfdump command on a crafted file.

## References
- http://www.securityfocus.com/bid/93595
- https://blogs.gentoo.org/ago/2016/10/04/libdwarf-heap-based-buffer-overflow-in-_dwarf_get_abbrev_for_code-dwarf_util-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1385686
- https://sourceforge.net/p/libdwarf/code/ci/268c1f18d1d28612af3b72d7c670076b1b88e51c/tree/libdwarf/dwarf_util.c?diff=0b28b923c3bd9827d1d904feed2abadde4fa5de2
- http://www.openwall.com/lists/oss-security/2016/10/16/4
