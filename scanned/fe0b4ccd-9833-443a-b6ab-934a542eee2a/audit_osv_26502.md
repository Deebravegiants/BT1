# [H] scsi: lpfc: Fix use-after-free KFENCE violation during sysfs firmware write

## Summary
Severity: High
Advisory: CVE-2023-53282
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53282
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Fix use-after-free KFENCE violation during sysfs firmware write

During the sysfs firmware write process, a use-after-free read warning is
logged from the lpfc_wr_object() routine:

  BUG: KFENCE: use-after-free read in lpfc_wr_object+0x235/0x310 [lpfc]
  Use-after-free read at 0x0000000000cf164d (in kfence-#111):
  lpfc_wr_object+0x235/0x310 [lpfc]
  lpfc_write_firmware.cold+0x206/0x30d [lpfc]
  lpfc_sli4_request_firmware_update+0xa6/0x100 [lpfc]
  lpfc_request_firmware_upgrade_store+0x66/0xb0 [lpfc]
  kernfs_fop_write_iter+0x121/0x1b0
  new_sync_write+0x11c/0x1b0
  vfs_write+0x1ef/0x280
  ksys_write+0x5f/0xe0
  do_syscall_64+0x59/0x90
  entry_SYSCALL_64_after_hwframe+0x63/0xcd

The driver accessed wr_object pointer data, which was initialized into
mailbox payload memory, after the mailbox object was released back to the
mailbox pool.

Fix by moving the mailbox free calls to the end of the routine ensuring
that we don't reference internal mailbox memory after release.

## References
- https://git.kernel.org/stable/c/21681b81b9ae548c5dae7ae00d931197a27f480c
- https://git.kernel.org/stable/c/51ab4eb1a25e73c7fc2ad9026520c4d8369c93cc
- https://git.kernel.org/stable/c/8becb97918f04bb177bc9c4e00c2bdb302e00944
- https://git.kernel.org/stable/c/8dfefa8f424ab208e552df1bfd008b732f3d0ad1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53282.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53282
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
