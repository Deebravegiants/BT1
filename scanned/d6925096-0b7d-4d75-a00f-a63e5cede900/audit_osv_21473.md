# [H] CVE-2021-43313

## Summary
Severity: High
Advisory: CVE-2021-43313
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2021-43313
Type: osv

## Details
A heap-based buffer overflow was discovered in upx, during the variable 'bucket' points to an inaccessible address. The issue is being triggered in the function PackLinuxElf32::invert_pt_dynamic at p_lx_elf.cpp:1688.

## References
- https://github.com/upx/upx/issues/378
