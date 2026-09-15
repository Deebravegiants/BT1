# [H] binder: fix UAF in binder_thread_release()

## Summary
Severity: High
Advisory: CVE-2026-64469
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64469
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix UAF in binder_thread_release()

When a thread exits, binder_thread_release() walks its transaction stack
to clear the t->from and t->to_proc that correspond with the exiting
thread. However, a process dying in parallel might attempt to kfree some
of these transactions. And if one of them has no associated t->to_proc,
the t->to_proc->inner_lock will not be acquired.

This means that transaction accesses in binder_thread_release() after
t->to_proc has been cleared might race with binder_free_transaction()
and cause a use-after-free error as reported by KASAN:

  ==================================================================
  BUG: KASAN: slab-use-after-free in binder_thread_release+0x5d0/0x798
  Write of size 8 at addr ffff000016627500 by task X/715

  CPU: 17 UID: 0 PID: 715 Comm: X Not tainted 7.1.0-rc5-00149-g8fde5d1d47f6 #30 PREEMPT
  Hardware name: linux,dummy-virt (DT)
  Call trace:
   binder_thread_release+0x5d0/0x798
   binder_ioctl+0x12c0/0x299c
   [...]

  Allocated by task 717 on cpu 18 at 67.267803s:
   __kasan_kmalloc+0xa0/0xbc
   __kmalloc_cache_noprof+0x174/0x444
   binder_transaction+0x554/0x8150
   binder_thread_write+0xa30/0x4354
   binder_ioctl+0x20f0/0x299c
   [...]

  Freed by task 202 on cpu 18 at 90.416221s:
   __kasan_slab_free+0x58/0x80
   kfree+0x1a0/0x4a4
   binder_free_transaction+0x150/0x294
   binder_send_failed_reply+0x398/0x6d8
   binder_release_work+0x3e4/0x4ec
   binder_deferred_func+0xbd8/0x104c
   [...]
  ==================================================================

In order to avoid this, make sure that binder_free_transaction() reads
the t->to_proc under the transaction lock. This will serialize the
transaction release with the accesses in binder_thread_release(). Plus,
it matches the documented locking rules for @to_proc.

## References
- https://git.kernel.org/stable/c/114a116aaa5f0295376cdf12da743c5bce3b20ce
- https://git.kernel.org/stable/c/1f96f8c0a6ed4f6d01d3dd29ad0cbf08dde96082
- https://git.kernel.org/stable/c/38e1a71728e5795b670cc159c18e286a40aeebb4
- https://git.kernel.org/stable/c/df1a17abba8d6fac5f965adcb8113ceace6e4949
- https://git.kernel.org/stable/c/e63032dc715026a96bcaa13d375a8e15c91caa84
- https://git.kernel.org/stable/c/ea02df466df60ecd758eb3b4df3f0cadc5c886ce
- https://git.kernel.org/stable/c/ef5439ba5b9ac93349f5df12ef88b42a0ce26340
- https://git.kernel.org/stable/c/faa070c7ad8ba25dcd0b12d7cdbb419e336f5391
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64469.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64469
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
