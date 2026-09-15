# [M] CVE-2021-47188

## Summary
Severity: Medium
Advisory: CVE-2021-47188
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47188
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: core: Improve SCSI abort handling

The following has been observed on a test setup:

WARNING: CPU: 4 PID: 250 at drivers/scsi/ufs/ufshcd.c:2737 ufshcd_queuecommand+0x468/0x65c
Call trace:
 ufshcd_queuecommand+0x468/0x65c
 scsi_send_eh_cmnd+0x224/0x6a0
 scsi_eh_test_devices+0x248/0x418
 scsi_eh_ready_devs+0xc34/0xe58
 scsi_error_handler+0x204/0x80c
 kthread+0x150/0x1b4
 ret_from_fork+0x10/0x30

That warning is triggered by the following statement:

	WARN_ON(lrbp->cmd);

Fix this warning by clearing lrbp->cmd from the abort handler.

## References
- https://git.kernel.org/stable/c/3ff1f6b6ba6f97f50862aa50e79959cc8ddc2566
- https://git.kernel.org/stable/c/c36baca06efa833adaefba61f45fefdc49b6d070
