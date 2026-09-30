# [C] CVE-2017-9054

## Summary
Severity: Critical
Advisory: CVE-2017-9054
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9054
Type: osv

## Details
An issue, also known as DW201703-002, was discovered in libdwarf 2017-03-21. In _dwarf_decode_s_leb128_chk() a byte pointer was dereferenced just before it was checked for being in bounds, leading to a heap-based buffer over-read.

## References
- https://www.prevanders.net/dwarfbug.html
