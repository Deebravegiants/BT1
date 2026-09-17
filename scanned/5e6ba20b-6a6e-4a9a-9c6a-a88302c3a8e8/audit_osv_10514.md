# [M] CVE-2017-16805

## Summary
Severity: Medium
Advisory: CVE-2017-16805
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-16805
Type: osv

## Details
In radare2 2.0.1, libr/bin/dwarf.c allows remote attackers to cause a denial of service (invalid read and application crash) via a crafted ELF file, related to r_bin_dwarf_parse_comp_unit in dwarf.c and sdb_set_internal in shlr/sdb/src/sdb.c.

## References
- https://github.com/radare/radare2/commit/2ca9ab45891b6ae8e32b6c28c81eebca059cbe5d
- https://github.com/radare/radare2/issues/8813
