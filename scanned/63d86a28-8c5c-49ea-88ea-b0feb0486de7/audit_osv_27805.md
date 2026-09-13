# [M] CVE-2024-26327

## Summary
Severity: Medium
Advisory: CVE-2024-26327
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-26327
Type: osv

## Details
An issue was discovered in QEMU 7.1.0 through 8.2.1. register_vfs in hw/pci/pcie_sriov.c mishandles the situation where a guest writes NumVFs greater than TotalVFs, leading to a buffer overflow in VF implementations.

## References
- https://lore.kernel.org/all/20240214-reuse-v4-5-89ad093a07f4%40daynix.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26327.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26327
- https://security.netapp.com/advisory/ntap-20240419-0010/
