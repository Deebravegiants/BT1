# [H] binder: fix node UAF in binder_add_freeze_work()

## Summary
Severity: High
Advisory: CVE-2024-56556
Aliases: A-380855429, ASB-A-380855429
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56556
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix node UAF in binder_add_freeze_work()

In binder_add_freeze_work() we iterate over the proc->nodes with the
proc->inner_lock held. However, this lock is temporarily dropped in
order to acquire the node->lock first (lock nesting order). This can
race with binder_node_release() and trigger a use-after-free:

  ==================================================================
  BUG: KASAN: slab-use-after-free in _raw_spin_lock+0xe4/0x19c
  Write of size 4 at addr ffff53c04c29dd04 by task freeze/640

  CPU: 5 UID: 0 PID: 640 Comm: freeze Not tainted 6.11.0-07343-ga727812a8d45 #17
  Hardware name: linux,dummy-virt (DT)
  Call trace:
   _raw_spin_lock+0xe4/0x19c
   binder_add_freeze_work+0x148/0x478
   binder_ioctl+0x1e70/0x25ac
   __arm64_sys_ioctl+0x124/0x190

  Allocated by task 637:
   __kmalloc_cache_noprof+0x12c/0x27c
   binder_new_node+0x50/0x700
   binder_transaction+0x35ac/0x6f74
   binder_thread_write+0xfb8/0x42a0
   binder_ioctl+0x18f0/0x25ac
   __arm64_sys_ioctl+0x124/0x190

  Freed by task 637:
   kfree+0xf0/0x330
   binder_thread_read+0x1e88/0x3a68
   binder_ioctl+0x16d8/0x25ac
   __arm64_sys_ioctl+0x124/0x190
  ==================================================================

Fix the race by taking a temporary reference on the node before
releasing the proc->inner lock. This ensures the node remains alive
while in use.

## References
- https://git.kernel.org/stable/c/38fbefeb2c140b581ed7de8117a5c90d6dd89c22
- https://git.kernel.org/stable/c/dc8aea47b928cc153b591b3558829ce42f685074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56556.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56556
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
