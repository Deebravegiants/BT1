# [M] nvme-pci: fix race condition between reset and nvme_dev_disable()

## Summary
Severity: Medium
Advisory: CVE-2024-50135
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50135
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: fix race condition between reset and nvme_dev_disable()

nvme_dev_disable() modifies the dev->online_queues field, therefore
nvme_pci_update_nr_queues() should avoid racing against it, otherwise
we could end up passing invalid values to blk_mq_update_nr_hw_queues().

 WARNING: CPU: 39 PID: 61303 at drivers/pci/msi/api.c:347
          pci_irq_get_affinity+0x187/0x210
 Workqueue: nvme-reset-wq nvme_reset_work [nvme]
 RIP: 0010:pci_irq_get_affinity+0x187/0x210
 Call Trace:
  <TASK>
  ? blk_mq_pci_map_queues+0x87/0x3c0
  ? pci_irq_get_affinity+0x187/0x210
  blk_mq_pci_map_queues+0x87/0x3c0
  nvme_pci_map_queues+0x189/0x460 [nvme]
  blk_mq_update_nr_hw_queues+0x2a/0x40
  nvme_reset_work+0x1be/0x2a0 [nvme]

Fix the bug by locking the shutdown_lock mutex before using
dev->online_queues. Give up if nvme_dev_disable() is running or if
it has been executed already.

## References
- https://git.kernel.org/stable/c/26bc0a81f64ce00fc4342c38eeb2eddaad084dd2
- https://git.kernel.org/stable/c/4ed32cc0939b64e3d7b48c8c0d63ea038775f304
- https://git.kernel.org/stable/c/b33e49a5f254474b33ce98fd45dd0ffdc247a0be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50135.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
