# [H] CVE-2021-43317

## Summary
Severity: High
Advisory: CVE-2021-43317
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2021-43317
Type: osv

## Details
A heap-based buffer overflows was discovered in upx, during the generic pointer 'p' points to an inaccessible address in func get_le32(). The problem is essentially caused in PackLinuxElf64::elf_lookup() at p_lx_elf.cpp:5404

## References
- https://github.com/upx/upx/issues/380
