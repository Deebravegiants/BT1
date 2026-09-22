# [M] CVE-2020-27788

## Summary
Severity: Medium
Advisory: CVE-2020-27788
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/CVE-2020-27788
Type: osv

## Details
An out-of-bounds read access vulnerability was discovered in UPX in PackLinuxElf64::canPack() function of p_lx_elf.cpp file. An attacker with a crafted input file could trigger this issue that could cause a crash leading to a denial of service.

## References
- https://github.com/upx/upx/commit/1bb93d4fce9f1d764ba57bf5ac154af515b3fc83
- https://github.com/upx/upx/issues/332
