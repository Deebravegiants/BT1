# [M] ext4: fix null-ptr-deref in ext4_write_info

## Summary
Severity: Medium
Advisory: CVE-2022-50344
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50344
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix null-ptr-deref in ext4_write_info

I caught a null-ptr-deref bug as follows:
==================================================================
KASAN: null-ptr-deref in range [0x0000000000000068-0x000000000000006f]
CPU: 1 PID: 1589 Comm: umount Not tainted 5.10.0-02219-dirty #339
RIP: 0010:ext4_write_info+0x53/0x1b0
[...]
Call Trace:
 dquot_writeback_dquots+0x341/0x9a0
 ext4_sync_fs+0x19e/0x800
 __sync_filesystem+0x83/0x100
 sync_filesystem+0x89/0xf0
 generic_shutdown_super+0x79/0x3e0
 kill_block_super+0xa1/0x110
 deactivate_locked_super+0xac/0x130
 deactivate_super+0xb6/0xd0
 cleanup_mnt+0x289/0x400
 __cleanup_mnt+0x16/0x20
 task_work_run+0x11c/0x1c0
 exit_to_user_mode_prepare+0x203/0x210
 syscall_exit_to_user_mode+0x5b/0x3a0
 do_syscall_64+0x59/0x70
 entry_SYSCALL_64_after_hwframe+0x44/0xa9
 ==================================================================

Above issue may happen as follows:
-------------------------------------
exit_to_user_mode_prepare
 task_work_run
  __cleanup_mnt
   cleanup_mnt
    deactivate_super
     deactivate_locked_super
      kill_block_super
       generic_shutdown_super
        shrink_dcache_for_umount
         dentry = sb->s_root
         sb->s_root = NULL              <--- Here set NULL
        sync_filesystem
         __sync_filesystem
          sb->s_op->sync_fs > ext4_sync_fs
           dquot_writeback_dquots
            sb->dq_op->write_info > ext4_write_info
             ext4_journal_start(d_inode(sb->s_root), EXT4_HT_QUOTA, 2)
              d_inode(sb->s_root)
               s_root->d_inode          <--- Null pointer dereference

To solve this problem, we use ext4_journal_start_sb directly
to avoid s_root being used.

## References
- https://git.kernel.org/stable/c/3638aa1c7d87c0ca0aef23cf58cae2c48e7daca4
- https://git.kernel.org/stable/c/4a657319cfabd6199fd0b7b65bbebf6ded7a11c1
- https://git.kernel.org/stable/c/533c60a0b97cee5daab376933f486207e6680fb7
- https://git.kernel.org/stable/c/947264e00c46de19a016fd81218118c708fed2f3
- https://git.kernel.org/stable/c/bb420e8afc854d2a1caaa23a0c129839acfb7888
- https://git.kernel.org/stable/c/dc451578446afd03c0c21913993c08898a691435
- https://git.kernel.org/stable/c/f34ab95162763cd7352f46df169296eec28b688d
- https://git.kernel.org/stable/c/f4b5ff0b794aa94afac7269c494550ca2f66511b
- https://git.kernel.org/stable/c/f9c1f248607d5546075d3f731e7607d5571f2b60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50344.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50344
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
