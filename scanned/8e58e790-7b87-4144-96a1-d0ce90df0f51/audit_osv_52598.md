# [M] CVE-2021-47622

## Summary
Severity: Medium
Advisory: CVE-2021-47622
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2021-47622
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: Fix a deadlock in the error handler

The following deadlock has been observed on a test setup:

 - All tags allocated

 - The SCSI error handler calls ufshcd_eh_host_reset_handler()

 - ufshcd_eh_host_reset_handler() queues work that calls
   ufshcd_err_handler()

 - ufshcd_err_handler() locks up as follows:

Workqueue: ufs_eh_wq_0 ufshcd_err_handler.cfi_jt
Call trace:
 __switch_to+0x298/0x5d8
 __schedule+0x6cc/0xa94
 schedule+0x12c/0x298
 blk_mq_get_tag+0x210/0x480
 __blk_mq_alloc_request+0x1c8/0x284
 blk_get_request+0x74/0x134
 ufshcd_exec_dev_cmd+0x68/0x640
 ufshcd_verify_dev_init+0x68/0x35c
 ufshcd_probe_hba+0x12c/0x1cb8
 ufshcd_host_reset_and_restore+0x88/0x254
 ufshcd_reset_and_restore+0xd0/0x354
 ufshcd_err_handler+0x408/0xc58
 process_one_work+0x24c/0x66c
 worker_thread+0x3e8/0xa4c
 kthread+0x150/0x1b4
 ret_from_fork+0x10/0x30

Fix this lockup by making ufshcd_exec_dev_cmd() allocate a reserved
request.

## References
- https://git.kernel.org/stable/c/945c3cca05d78351bba29fa65d93834cb7934c7b
- https://git.kernel.org/stable/c/d69d98d8edf90e25e4e09930dd36dd6d09dd6768
- https://git.kernel.org/stable/c/493c9e850677df8b4eda150c2364b1c1a72ed724
