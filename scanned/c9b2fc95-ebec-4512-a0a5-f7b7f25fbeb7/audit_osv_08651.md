# [H] CVE-2016-5038

## Summary
Severity: High
Advisory: CVE-2016-5038
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-5038
Type: osv

## Details
The dwarf_get_macro_startend_file function in dwarf_macro5.c in libdwarf before 20160923 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted string offset for .debug_str.

## References
- https://www.prevanders.net/dwarfbug.html
- http://www.openwall.com/lists/oss-security/2016/05/24/1
- http://www.openwall.com/lists/oss-security/2016/05/25/1
