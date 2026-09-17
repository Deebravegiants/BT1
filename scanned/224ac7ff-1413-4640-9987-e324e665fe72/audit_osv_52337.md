# [M] CVE-2021-47343

## Summary
Severity: Medium
Advisory: CVE-2021-47343
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47343
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm btree remove: assign new_root only when removal succeeds

remove_raw() in dm_btree_remove() may fail due to IO read error
(e.g. read the content of origin block fails during shadowing),
and the value of shadow_spine::root is uninitialized, but
the uninitialized value is still assign to new_root in the
end of dm_btree_remove().

For dm-thin, the value of pmd->details_root or pmd->root will become
an uninitialized value, so if trying to read details_info tree again
out-of-bound memory may occur as showed below:

  general protection fault, probably for non-canonical address 0x3fdcb14c8d7520
  CPU: 4 PID: 515 Comm: dmsetup Not tainted 5.13.0-rc6
  Hardware name: QEMU Standard PC
  RIP: 0010:metadata_ll_load_ie+0x14/0x30
  Call Trace:
   sm_metadata_count_is_more_than_one+0xb9/0xe0
   dm_tm_shadow_block+0x52/0x1c0
   shadow_step+0x59/0xf0
   remove_raw+0xb2/0x170
   dm_btree_remove+0xf4/0x1c0
   dm_pool_delete_thin_device+0xc3/0x140
   pool_message+0x218/0x2b0
   target_message+0x251/0x290
   ctl_ioctl+0x1c4/0x4d0
   dm_ctl_ioctl+0xe/0x20
   __x64_sys_ioctl+0x7b/0xb0
   do_syscall_64+0x40/0xb0
   entry_SYSCALL_64_after_hwframe+0x44/0xae

Fixing it by only assign new_root when removal succeeds

## References
- https://git.kernel.org/stable/c/4c84b3e0728ffe10d89c633694c35a02b5c477dc
- https://git.kernel.org/stable/c/89bf942314b78d454db92427201421b5dec132d9
- https://git.kernel.org/stable/c/8fbae4a1bdb5b889490cdee929e68540151536e5
- https://git.kernel.org/stable/c/ad365e9351ac2b450e7e79932ff6abf59342d91a
- https://git.kernel.org/stable/c/ba47e65a5de3e0e8270301a409fc63d3129fdb9e
- https://git.kernel.org/stable/c/73f27adaa73e3057a9ec464e33c4f54d34ea5de3
- https://git.kernel.org/stable/c/964d57d1962d7e68f0f578f05d9ae4a104d74851
- https://git.kernel.org/stable/c/b6e58b5466b2959f83034bead2e2e1395cca8aeb
- https://git.kernel.org/stable/c/c154775619186781aaf8a99333ac07437a1768d5
