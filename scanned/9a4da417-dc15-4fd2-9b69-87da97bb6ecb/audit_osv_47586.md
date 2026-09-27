# [M] CVE-2016-8681

## Summary
Severity: Medium
Advisory: CVE-2016-8681
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8681
Type: osv

## Details
The _dwarf_get_abbrev_for_code function in dwarf_util.c in libdwarf 20161001 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) by calling the dwarfdump command on a crafted file.

## References
- http://www.securityfocus.com/bid/93592
- https://bugzilla.redhat.com/show_bug.cgi?id=1385690
- http://www.openwall.com/lists/oss-security/2016/10/16/5
- https://blogs.gentoo.org/ago/2016/10/06/libdwarf-heap-based-buffer-overflow-in-_dwarf_get_abbrev_for_code-dwarf_util-c-2/
