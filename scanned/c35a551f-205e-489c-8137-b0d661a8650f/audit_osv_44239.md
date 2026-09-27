# [H] scsi: hisi_sas: Add slave_destroy interface for v3 hw

## Summary
Severity: High
Advisory: CVE-2026-80653
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80653
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: hisi_sas: Add slave_destroy interface for v3 hw

WARNING is triggered when executing link reset of remote PHY and rmmod
SAS driver simultaneously. Following is the WARNING log:

WARNING: CPU: 61 PID: 21818 at drivers/base/core.c:1347 __device_links_no_driver+0xb4/0xc0
 Call trace:
  __device_links_no_driver+0xb4/0xc0
  device_links_driver_cleanup+0xb0/0xfc
  __device_release_driver+0x198/0x23c
  device_release_driver+0x38/0x50
  bus_remove_device+0x130/0x140
  device_del+0x184/0x434
  __scsi_remove_device+0x118/0x150
  scsi_remove_target+0x1bc/0x240
  sas_rphy_remove+0x90/0x94
  sas_rphy_delete+0x24/0x3c
  sas_destruct_devices+0x64/0xa0 [libsas]
  sas_revalidate_domain+0xe4/0x150 [libsas]
  process_one_work+0x1e0/0x46c
  worker_thread+0x15c/0x464
  kthread+0x160/0x170
  ret_from_fork+0x10/0x20
 ---[ end trace 71e059eb58f85d4a ]---

During SAS phy up, link->status is set to DL_STATE_AVAILABLE in
device_links_driver_bound, then this setting influences
__device_links_no_driver() before driver rmmod and caused WARNING.

Add the slave_destroy interface to make sure link is removed after flush
workque.

## References
- https://git.kernel.org/stable/c/4867dba229292e13fc19ed865ec1839661952ff9
- https://git.kernel.org/stable/c/67b85a88265df19f049241d8c00571a5408f4eeb
- https://git.kernel.org/stable/c/cb414aff28e18e6f5cff9f87ea31376ed8af317b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80653.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80653
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
