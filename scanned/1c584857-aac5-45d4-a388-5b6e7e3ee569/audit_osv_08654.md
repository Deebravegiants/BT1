# [H] CVE-2016-5041

## Summary
Severity: High
Advisory: CVE-2016-5041
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2016-5041
Type: osv

## Details
dwarf_macro5.c in libdwarf before 20160923 allows remote attackers to cause a denial of service (NULL pointer dereference) via a debugging information entry using DWARF5 and without a DW_AT_name.

## References
- https://www.prevanders.net/dwarfbug.html
- http://www.openwall.com/lists/oss-security/2016/05/24/1
- http://www.openwall.com/lists/oss-security/2016/05/25/1
