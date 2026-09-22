# [H] scsi: ufs: core: Fix device management cmd timeout flow

## Summary
Severity: High
Advisory: CVE-2023-53387
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53387
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: core: Fix device management cmd timeout flow

In the UFS error handling flow, the host will send a device management cmd
(NOP OUT) to the device for link recovery. If this cmd times out and
clearing the doorbell fails, ufshcd_wait_for_dev_cmd() will do nothing and
return. hba->dev_cmd.complete struct is not set to NULL.

When this happens, if cmd has been completed by device, then we will call
complete() in __ufshcd_transfer_req_compl(). Because the complete struct is
allocated on the stack, the following crash will occur:

  ipanic_die+0x24/0x38 [mrdump]
  die+0x344/0x748
  arm64_notify_die+0x44/0x104
  do_debug_exception+0x104/0x1e0
  el1_dbg+0x38/0x54
  el1_sync_handler+0x40/0x88
  el1_sync+0x8c/0x140
  queued_spin_lock_slowpath+0x2e4/0x3c0
  __ufshcd_transfer_req_compl+0x3b0/0x1164
  ufshcd_trc_handler+0x15c/0x308
  ufshcd_host_reset_and_restore+0x54/0x260
  ufshcd_reset_and_restore+0x28c/0x57c
  ufshcd_err_handler+0xeb8/0x1b6c
  process_one_work+0x288/0x964
  worker_thread+0x4bc/0xc7c
  kthread+0x15c/0x264
  ret_from_fork+0x10/0x30

## References
- https://git.kernel.org/stable/c/36822124f9de200cedc2f42516301b50d386a6cd
- https://git.kernel.org/stable/c/3ffd2cd644e0f1eea01339831bac4b1054e8817c
- https://git.kernel.org/stable/c/cf45493432704786a0f8294c7723ad4eeb5fff24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53387.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53387
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
