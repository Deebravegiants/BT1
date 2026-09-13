# [M] CVE-2018-14015

## Summary
Severity: Medium
Advisory: CVE-2018-14015
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-12
Source: https://osv.dev/vulnerability/CVE-2018-14015
Type: osv

## Details
The sdb_set_internal function in sdb.c in radare2 2.7.0 allows remote attackers to cause a denial of service (invalid read and application crash) via a crafted ELF file because of missing input validation in r_bin_dwarf_parse_comp_unit in libr/bin/dwarf.c.

## References
- https://github.com/radareorg/radare2/commit/d37d2b858ac47f2f108034be0bcecadaddfbc8b3
- https://github.com/radare/radare2/issues/10465
