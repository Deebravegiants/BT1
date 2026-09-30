# [C] CVE-2016-9480

## Summary
Severity: Critical
Advisory: CVE-2016-9480
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-11-29
Source: https://osv.dev/vulnerability/CVE-2016-9480
Type: osv

## Details
libdwarf 2016-10-21 allows context-dependent attackers to obtain sensitive information or cause a denial of service by using the "malformed dwarf file" approach, related to a "Heap Buffer Over-read" issue affecting the dwarf_util.c component, aka DW201611-006.

## References
- http://www.securityfocus.com/bid/94980
- https://www.prevanders.net/dwarfbug.html
- https://sourceforge.net/p/libdwarf/bugs/5/
- https://sourceforge.net/p/libdwarf/code/ci/5dd64de047cd5ec479fb11fe7ff2692fd819e5e5/
