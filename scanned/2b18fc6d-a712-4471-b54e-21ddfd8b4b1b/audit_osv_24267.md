# [H] udf: Avoid double brelse() in udf_rename()

## Summary
Severity: High
Advisory: CVE-2022-50755
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50755
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Avoid double brelse() in udf_rename()

syzbot reported a warning like below [1]:

VFS: brelse: Trying to free free buffer
WARNING: CPU: 2 PID: 7301 at fs/buffer.c:1145 __brelse+0x67/0xa0
...
Call Trace:
 <TASK>
 invalidate_bh_lru+0x99/0x150
 smp_call_function_many_cond+0xe2a/0x10c0
 ? generic_remap_file_range_prep+0x50/0x50
 ? __brelse+0xa0/0xa0
 ? __mutex_lock+0x21c/0x12d0
 ? smp_call_on_cpu+0x250/0x250
 ? rcu_read_lock_sched_held+0xb/0x60
 ? lock_release+0x587/0x810
 ? __brelse+0xa0/0xa0
 ? generic_remap_file_range_prep+0x50/0x50
 on_each_cpu_cond_mask+0x3c/0x80
 blkdev_flush_mapping+0x13a/0x2f0
 blkdev_put_whole+0xd3/0xf0
 blkdev_put+0x222/0x760
 deactivate_locked_super+0x96/0x160
 deactivate_super+0xda/0x100
 cleanup_mnt+0x222/0x3d0
 task_work_run+0x149/0x240
 ? task_work_cancel+0x30/0x30
 do_exit+0xb29/0x2a40
 ? reacquire_held_locks+0x4a0/0x4a0
 ? do_raw_spin_lock+0x12a/0x2b0
 ? mm_update_next_owner+0x7c0/0x7c0
 ? rwlock_bug.part.0+0x90/0x90
 ? zap_other_threads+0x234/0x2d0
 do_group_exit+0xd0/0x2a0
 __x64_sys_exit_group+0x3a/0x50
 do_syscall_64+0x34/0xb0
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

The cause of the issue is that brelse() is called on both ofibh.sbh
and ofibh.ebh by udf_find_entry() when it returns NULL.  However,
brelse() is called by udf_rename(), too.  So, b_count on buffer_head
becomes unbalanced.

This patch fixes the issue by not calling brelse() by udf_rename()
when udf_find_entry() returns NULL.

## References
- https://git.kernel.org/stable/c/090bf49833c51da297ec74f98ad2bf44daea9311
- https://git.kernel.org/stable/c/156d440dea97deada629bb51cb17887abd862605
- https://git.kernel.org/stable/c/40dba68d418237b1ae2beaa06d46a94dd946278e
- https://git.kernel.org/stable/c/4fca09045509f5bde8fc28e68fbca38cb4bdcf2e
- https://git.kernel.org/stable/c/78eba2778ae10fb2a9d450e14d26eb6f6bf1f906
- https://git.kernel.org/stable/c/9d2cad69547abea961fa80426d600b861de1952b
- https://git.kernel.org/stable/c/c791730f2554a9ebb8f18df9368dc27d4ebc38c2
- https://git.kernel.org/stable/c/d6da7ec0f94f5208c848e0e94b70f54a0bd9c587
- https://git.kernel.org/stable/c/e7a6a53c871460727be09f4414ccb29fb8697526
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50755.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
