# [M] CVE-2016-5035

## Summary
Severity: Medium
Advisory: CVE-2016-5035
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-5035
Type: osv

## Details
The _dwarf_read_line_table_header function in dwarf_line_table_reader.c in libdwarf before 20160923 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file.

## References
- https://www.prevanders.net/dwarfbug.html
- http://www.openwall.com/lists/oss-security/2016/05/24/1
- http://www.openwall.com/lists/oss-security/2016/05/25/1
