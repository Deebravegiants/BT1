# [C] CVE-2017-9052

## Summary
Severity: Critical
Advisory: CVE-2017-9052
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9052
Type: osv

## Details
An issue, also known as DW201703-006, was discovered in libdwarf 2017-03-21. A heap-based buffer over-read in dwarf_formsdata() is due to a failure to check a pointer for being in bounds (in a few places in this function) and a failure in a check in dwarf_attr_list().

## References
- https://www.prevanders.net/dwarfbug.html
- http://www.securityfocus.com/bid/98553
