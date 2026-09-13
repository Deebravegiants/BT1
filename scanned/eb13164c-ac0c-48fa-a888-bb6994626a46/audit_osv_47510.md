# [M] CVE-2016-7410

## Summary
Severity: Medium
Advisory: CVE-2016-7410
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-7410
Type: osv

## Details
The _dwarf_read_loc_section function in dwarf_loc.c in libdwarf 20160613 allows attackers to cause a denial of service (buffer over-read) via a crafted file.

## References
- http://www.openwall.com/lists/oss-security/2016/09/15/3
- http://www.securityfocus.com/bid/92971
- http://www.openwall.com/lists/oss-security/2016/09/13/5
