# [H] nfs/blocklayout: Don't attempt unregister for invalid block device

## Summary
Severity: High
Advisory: CVE-2024-53167
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53167
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs/blocklayout: Don't attempt unregister for invalid block device

Since commit d869da91cccb ("nfs/blocklayout: Fix premature PR key
unregistration") an unmount of a pNFS SCSI layout-enabled NFS may
dereference a NULL block_device in:

  bl_unregister_scsi+0x16/0xe0 [blocklayoutdriver]
  bl_free_device+0x70/0x80 [blocklayoutdriver]
  bl_free_deviceid_node+0x12/0x30 [blocklayoutdriver]
  nfs4_put_deviceid_node+0x60/0xc0 [nfsv4]
  nfs4_deviceid_purge_client+0x132/0x190 [nfsv4]
  unset_pnfs_layoutdriver+0x59/0x60 [nfsv4]
  nfs4_destroy_server+0x36/0x70 [nfsv4]
  nfs_free_server+0x23/0xe0 [nfs]
  deactivate_locked_super+0x30/0xb0
  cleanup_mnt+0xba/0x150
  task_work_run+0x59/0x90
  syscall_exit_to_user_mode+0x217/0x220
  do_syscall_64+0x8e/0x160

This happens because even though we were able to create the
nfs4_deviceid_node, the lookup for the device was unable to attach the
block device to the pnfs_block_dev.

If we never found a block device to register, we can avoid this case with
the PNFS_BDEV_REGISTERED flag.  Move the deref behind the test for the
flag.

## References
- https://git.kernel.org/stable/c/3402704a424f34bbcca7f4a4503859357f422217
- https://git.kernel.org/stable/c/3a4ce14d9a6b868e0787e4582420b721c04ee41e
- https://git.kernel.org/stable/c/faa4bacfaeed827a4ca8cb8529a3ce65a9e8ef46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53167.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53167
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
