# [H] binder: fix UAF in binder_netlink_report()

## Summary
Severity: High
Advisory: CVE-2026-23184
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23184
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix UAF in binder_netlink_report()

Oneway transactions sent to frozen targets via binder_proc_transaction()
return a BR_TRANSACTION_PENDING_FROZEN error but they are still treated
as successful since the target is expected to thaw at some point. It is
then not safe to access 't' after BR_TRANSACTION_PENDING_FROZEN errors
as the transaction could have been consumed by the now thawed target.

This is the case for binder_netlink_report() which derreferences 't'
after a pending frozen error, as pointed out by the following KASAN
report:

  ==================================================================
  BUG: KASAN: slab-use-after-free in binder_netlink_report.isra.0+0x694/0x6c8
  Read of size 8 at addr ffff00000f98ba38 by task binder-util/522

  CPU: 4 UID: 0 PID: 522 Comm: binder-util Not tainted 6.19.0-rc6-00015-gc03e9c42ae8f #1 PREEMPT
  Hardware name: linux,dummy-virt (DT)
  Call trace:
   binder_netlink_report.isra.0+0x694/0x6c8
   binder_transaction+0x66e4/0x79b8
   binder_thread_write+0xab4/0x4440
   binder_ioctl+0x1fd4/0x2940
   [...]

  Allocated by task 522:
   __kmalloc_cache_noprof+0x17c/0x50c
   binder_transaction+0x584/0x79b8
   binder_thread_write+0xab4/0x4440
   binder_ioctl+0x1fd4/0x2940
   [...]

  Freed by task 488:
   kfree+0x1d0/0x420
   binder_free_transaction+0x150/0x234
   binder_thread_read+0x2d08/0x3ce4
   binder_ioctl+0x488/0x2940
   [...]
  ==================================================================

Instead, make a transaction copy so the data can be safely accessed by
binder_netlink_report() after a pending frozen error. While here, add a
comment about not using t->buffer in binder_netlink_report().

## References
- https://git.kernel.org/stable/c/5e8a3d01544282e50d887d76f30d1496a0a53562
- https://git.kernel.org/stable/c/a6050dedb6f1cc23e518e3a132ab74a0aad6df90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23184.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
