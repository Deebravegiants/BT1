# [M] CVE-2020-16269

## Summary
Severity: Medium
Advisory: CVE-2020-16269
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-03
Source: https://osv.dev/vulnerability/CVE-2020-16269
Type: osv

## Details
radare2 4.5.0 misparses DWARF information in executable files, causing a segmentation fault in parse_typedef in type_dwarf.c via a malformed DW_AT_name in the .debug_info section.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45SGGCWFIIV7N2X2QZRREHOW7ODT3IH7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZJET3RR6W7LAK4H6VPTMAZS24W7XYHRZ/
- https://github.com/radareorg/radare2/issues/17383
