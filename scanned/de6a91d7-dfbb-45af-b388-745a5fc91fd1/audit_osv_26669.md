# [H] scsi: ufs: core: Fix handling of lrbp->cmd

## Summary
Severity: High
Advisory: CVE-2023-53510
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53510
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.1.167, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: core: Fix handling of lrbp->cmd

ufshcd_queuecommand() may be called two times in a row for a SCSI command
before it is completed. Hence make the following changes:

 - In the functions that submit a command, do not check the old value of
   lrbp->cmd nor clear lrbp->cmd in error paths.

 - In ufshcd_release_scsi_cmd(), do not clear lrbp->cmd.

See also scsi_send_eh_cmnd().

This commit prevents that the following appears if a command times out:

WARNING: at drivers/ufs/core/ufshcd.c:2965 ufshcd_queuecommand+0x6f8/0x9a8
Call trace:
 ufshcd_queuecommand+0x6f8/0x9a8
 scsi_send_eh_cmnd+0x2c0/0x960
 scsi_eh_test_devices+0x100/0x314
 scsi_eh_ready_devs+0xd90/0x114c
 scsi_error_handler+0x2b4/0xb70
 kthread+0x16c/0x1e0

## References
- https://git.kernel.org/stable/c/49234a401e161a2f2698f4612ab792c49b3cad1b
- https://git.kernel.org/stable/c/549e91a9bbaa0ee480f59357868421a61d369770
- https://git.kernel.org/stable/c/b6d76d63c6d21d5d26c301a46853a2aee72397d5
- https://git.kernel.org/stable/c/f3ee24af62681b942bbd799ac77b90a6d7e1fdb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53510.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53510
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
