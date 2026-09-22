# [M] CVE-2016-5028

## Summary
Severity: Medium
Advisory: CVE-2016-5028
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-5028
Type: osv

## Details
The print_frame_inst_bytes function in libdwarf before 20160923 allows remote attackers to cause a denial of service (NULL pointer dereference) via an object file with empty bss-like sections.

## References
- https://www.prevanders.net/dwarfbug.html
- http://www.openwall.com/lists/oss-security/2016/05/24/1
- http://www.openwall.com/lists/oss-security/2016/05/25/1
