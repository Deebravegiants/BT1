# [H] binder: fix UAF in binder_free_transaction()

## Summary
Severity: High
Advisory: CVE-2026-64468
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64468
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix UAF in binder_free_transaction()

In binder_free_transaction(), the t->to_proc is read under the t->lock.
However, once the t->lock is dropped, the to_proc can die in parallel.
This leads to a use-after-free error when we attempt to acquire its
inner lock right afterwards:

  ==================================================================
  BUG: KASAN: slab-use-after-free in _raw_spin_lock+0xe4/0x1a0
  Write of size 4 at addr ffff00001125da70 by task B/672

  CPU: 20 UID: 0 PID: 672 Comm: B Not tainted 7.1.0-rc6-00284-g8e65320d91cd #4 PREEMPT
  Hardware name: linux,dummy-virt (DT)
  Call trace:
   _raw_spin_lock+0xe4/0x1a0
   binder_free_transaction+0x8c/0x320
   binder_send_failed_reply+0x21c/0x2f8
   binder_thread_release+0x488/0x7e0
   binder_ioctl+0x12c0/0x29a0
  [...]

  Allocated by task 675:
   __kmalloc_cache_noprof+0x174/0x444
   binder_open+0x118/0xb70
   do_dentry_open+0x374/0x1040
   vfs_open+0x58/0x3bc
  [...]

  Freed by task 212:
   __kasan_slab_free+0x58/0x80
   kfree+0x1a0/0x4a4
   binder_proc_dec_tmpref+0x32c/0x5e0
   binder_deferred_func+0xc48/0x104c
   process_one_work+0x53c/0xbc0
  [...]
  ==================================================================

To prevent this, pin the target thread (t->to_thread) to guarantee the
target process remains alive. Undelivered transactions without a target
thread are already safe, as the target process can only be the current
context in those paths.

## References
- https://git.kernel.org/stable/c/0be901ab1dcc4af59b88f2e324493bb283850167
- https://git.kernel.org/stable/c/0f15f0f6ca5df566275ce517f257af2559528b41
- https://git.kernel.org/stable/c/328ccf32acb87e8bbb1fe2b065068c574e4db2bf
- https://git.kernel.org/stable/c/45df558c543bb5543bacc8065fd7c567740781e5
- https://git.kernel.org/stable/c/48aeda9f8039e4a6971d1804578efde7f2c01eda
- https://git.kernel.org/stable/c/5602a43f251c3d75312df91a422675fc00ca3dce
- https://git.kernel.org/stable/c/d45ef513eed1abebfec90c3cfb6ae50c2a4182db
- https://git.kernel.org/stable/c/f223d27a546c1e1f48d38fd67760e78f068fe8c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64468.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64468
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
