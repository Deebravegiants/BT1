# [H] wifi: ath12k: fix uaf in ath12k_core_init()

## Summary
Severity: High
Advisory: CVE-2025-38116
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38116
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix uaf in ath12k_core_init()

When the execution of ath12k_core_hw_group_assign() or
ath12k_core_hw_group_create() fails, the registered notifier chain is not
unregistered properly. Its memory is freed after rmmod, which may trigger
to a use-after-free (UAF) issue if there is a subsequent access to this
notifier chain.

Fixes the issue by calling ath12k_core_panic_notifier_unregister() in
failure cases.

Call trace:
 notifier_chain_register+0x4c/0x1f0 (P)
 atomic_notifier_chain_register+0x38/0x68
 ath12k_core_init+0x50/0x4e8 [ath12k]
 ath12k_pci_probe+0x5f8/0xc28 [ath12k]
 pci_device_probe+0xbc/0x1a8
 really_probe+0xc8/0x3a0
 __driver_probe_device+0x84/0x1b0
 driver_probe_device+0x44/0x130
 __driver_attach+0xcc/0x208
 bus_for_each_dev+0x84/0x100
 driver_attach+0x2c/0x40
 bus_add_driver+0x130/0x260
 driver_register+0x70/0x138
 __pci_register_driver+0x68/0x80
 ath12k_pci_init+0x30/0x68 [ath12k]
 ath12k_init+0x28/0x78 [ath12k]

Tested-on: WCN7850 hw2.0 PCI WLAN.HMT.1.0.c5-00481-QCAHMTSWPL_V1.0_V2.0_SILICONZ-3

## References
- https://git.kernel.org/stable/c/65e1b3404c211dcfaea02698539cdcd26647130f
- https://git.kernel.org/stable/c/f3fe49dbddd73f0155a8935af47cb63693069dbe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38116.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
