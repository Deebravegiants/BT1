# [M] CVE-2024-26328

## Summary
Severity: Medium
Advisory: CVE-2024-26328
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-26328
Type: osv

## Details
An issue was discovered in QEMU 7.1.0 through 8.2.1. register_vfs in hw/pci/pcie_sriov.c does not set NumVFs to PCI_SRIOV_TOTAL_VF, and thus interaction with hw/nvme/ctrl.c is mishandled.

## References
- https://lore.kernel.org/all/20240213055345-mutt-send-email-mst%40kernel.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26328.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26328
- https://security.netapp.com/advisory/ntap-20240419-0010/
