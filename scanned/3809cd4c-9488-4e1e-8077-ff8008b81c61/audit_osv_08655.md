# [H] CVE-2016-5042

## Summary
Severity: High
Advisory: CVE-2016-5042
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-5042
Type: osv

## Details
The dwarf_get_aranges_list function in libdwarf before 20160923 allows remote attackers to cause a denial of service (infinite loop and crash) via a crafted DWARF section.

## References
- https://www.prevanders.net/dwarfbug.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1332145
- http://www.openwall.com/lists/oss-security/2016/05/24/1
- http://www.openwall.com/lists/oss-security/2016/05/25/1
