# [M] wifi: iwlwifi: pcie: fix NULL pointer dereference in iwl_pcie_irq_rx_msix_handler()

## Summary
Severity: Medium
Advisory: CVE-2023-53251
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53251
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: pcie: fix NULL pointer dereference in iwl_pcie_irq_rx_msix_handler()

rxq can be NULL only when trans_pcie->rxq is NULL and entry->entry
is zero. For the case when entry->entry is not equal to 0, rxq
won't be NULL even if trans_pcie->rxq is NULL. Modify checker to
check for trans_pcie->rxq.

## References
- https://git.kernel.org/stable/c/1902f1953b8ba100ee8705cb8a6f1a9795550eca
- https://git.kernel.org/stable/c/2d690495eb2766d58e25c83676f422219c4fcf18
- https://git.kernel.org/stable/c/390e44efcf4d390b5053ad112553155d2d097c73
- https://git.kernel.org/stable/c/3b9de981fe7f1c6e07c7b852421ad69be3d4b6c2
- https://git.kernel.org/stable/c/f71d0fc407dd028416bec002ddcc62f5acb0346a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53251.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53251
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
