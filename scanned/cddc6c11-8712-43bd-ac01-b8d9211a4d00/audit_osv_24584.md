# [M] Upx: segv on packlinuxelf64::invert_pt_dynamic() in p_lx_elf.cpp

## Summary
Severity: Medium
Advisory: CVE-2023-23457
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2023-23457
Type: osv

## Details
A Segmentation fault was found in UPX in PackLinuxElf64::invert_pt_dynamic() in p_lx_elf.cpp. An attacker with a crafted input file allows invalid memory address access that could lead to a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23457.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EL3BVKIGG3SH6I3KPOYQAWCBD4UMPOPI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TGEP3FBNRZXGLIA2B2ICMB32JVMPREFZ/
- https://nvd.nist.gov/vuln/detail/CVE-2023-23457
- https://bugzilla.redhat.com/show_bug.cgi?id=2160382
- https://github.com/upx/upx/issues/631
- https://github.com/upx/upx/commit/779b648c5f6aa9b33f4728f79dd4d0efec0bf860
- https://github.com/upx/upx
