# [M] CVE-2019-20051

## Summary
Severity: Medium
Advisory: CVE-2019-20051
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-27
Source: https://osv.dev/vulnerability/CVE-2019-20051
Type: osv

## Details
A floating-point exception was discovered in PackLinuxElf::elf_hash in p_lx_elf.cpp in UPX 3.95. The vulnerability causes an application crash, which leads to denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D7XU42G6MUQQXHWRP7DCF2JSIBOJ5GOO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EUTVSTXAFTD552NO2K2RIF6MDQEHP3BE/
- https://github.com/upx/upx/issues/313
