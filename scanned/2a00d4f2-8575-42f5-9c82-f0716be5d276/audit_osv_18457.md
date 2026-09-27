# [M] CVE-2020-27790

## Summary
Severity: Medium
Advisory: CVE-2020-27790
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/CVE-2020-27790
Type: osv

## Details
A floating point exception issue was discovered in UPX in PackLinuxElf64::invert_pt_dynamic() function of p_lx_elf.cpp file. An attacker with a crafted input file could trigger this issue that could cause a crash leading to a denial of service. The highest impact is to Availability.

## References
- https://github.com/upx/upx/commit/eb90eab6325d009004ffb155e3e33f22d4d3ca26
- https://github.com/upx/upx/issues/331
