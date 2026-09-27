# [M] CVE-2018-11380

## Summary
Severity: Medium
Advisory: CVE-2018-11380
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11380
Type: osv

## Details
The parse_import_ptr() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted Mach-O file.

## References
- https://github.com/radare/radare2/issues/9970
- https://github.com/radare/radare2/commit/60208765887f5f008b3b9a883f3addc8bdb9c134
