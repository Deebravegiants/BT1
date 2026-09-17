# [M] CVE-2020-27787

## Summary
Severity: Medium
Advisory: CVE-2020-27787
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/CVE-2020-27787
Type: osv

## Details
A Segmentaation fault was found in UPX in invert_pt_dynamic() function in p_lx_elf.cpp. An attacker with a crafted input file allows invalid memory address access that could lead to a denial of service.

## References
- https://github.com/upx/upx/commit/e2f60adc95334f47e286838dac33160819c5d74d
- https://github.com/upx/upx/issues/333
