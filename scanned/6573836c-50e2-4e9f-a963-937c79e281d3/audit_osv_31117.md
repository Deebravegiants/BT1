# [H] wifi: ath12k: fix read pointer after free in ath12k_mac_assign_vif_to_vdev()

## Summary
Severity: High
Advisory: CVE-2024-57995
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57995
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.57, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix read pointer after free in ath12k_mac_assign_vif_to_vdev()

In ath12k_mac_assign_vif_to_vdev(), if arvif is created on a different
radio, it gets deleted from that radio through a call to
ath12k_mac_unassign_link_vif(). This action frees the arvif pointer.
Subsequently, there is a check involving arvif, which will result in a
read-after-free scenario.

Fix this by moving this check after arvif is again assigned via call to
ath12k_mac_assign_link_vif().

Tested-on: QCN9274 hw2.0 PCI WLAN.WBE.1.3.1-00173-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/57100b87c77818cb0d582a92e5cb32fff85c757d
- https://git.kernel.org/stable/c/5a10971c7645a95f5d5dc23c26fbac4bf61801d0
- https://git.kernel.org/stable/c/f3a95a312419e4f1e992525917da9dbcd247038f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57995.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57995
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
