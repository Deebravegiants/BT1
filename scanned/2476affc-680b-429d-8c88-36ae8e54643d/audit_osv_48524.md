# [C] CVE-2017-9055

## Summary
Severity: Critical
Advisory: CVE-2017-9055
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9055
Type: osv

## Details
An issue, also known as DW201703-001, was discovered in libdwarf 2017-03-21. In dwarf_formsdata() a few data types were not checked for being in bounds, leading to a heap-based buffer over-read.

## References
- https://www.prevanders.net/dwarfbug.html
