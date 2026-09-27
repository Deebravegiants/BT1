# [H] binder: fix UAF of ref->proc caused by race condition

## Summary
Severity: High
Advisory: CVE-2022-49939
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49939
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.14.293, >=4.15.0 <4.19.258, >=4.20.0 <5.4.213, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix UAF of ref->proc caused by race condition

A transaction of type BINDER_TYPE_WEAK_HANDLE can fail to increment the
reference for a node. In this case, the target proc normally releases
the failed reference upon close as expected. However, if the target is
dying in parallel the call will race with binder_deferred_release(), so
the target could have released all of its references by now leaving the
cleanup of the new failed reference unhandled.

The transaction then ends and the target proc gets released making the
ref->proc now a dangling pointer. Later on, ref->node is closed and we
attempt to take spin_lock(&ref->proc->inner_lock), which leads to the
use-after-free bug reported below. Let's fix this by cleaning up the
failed reference on the spot instead of relying on the target to do so.

  ==================================================================
  BUG: KASAN: use-after-free in _raw_spin_lock+0xa8/0x150
  Write of size 4 at addr ffff5ca207094238 by task kworker/1:0/590

  CPU: 1 PID: 590 Comm: kworker/1:0 Not tainted 5.19.0-rc8 #10
  Hardware name: linux,dummy-virt (DT)
  Workqueue: events binder_deferred_func
  Call trace:
   dump_backtrace.part.0+0x1d0/0x1e0
   show_stack+0x18/0x70
   dump_stack_lvl+0x68/0x84
   print_report+0x2e4/0x61c
   kasan_report+0xa4/0x110
   kasan_check_range+0xfc/0x1a4
   __kasan_check_write+0x3c/0x50
   _raw_spin_lock+0xa8/0x150
   binder_deferred_func+0x5e0/0x9b0
   process_one_work+0x38c/0x5f0
   worker_thread+0x9c/0x694
   kthread+0x188/0x190
   ret_from_fork+0x10/0x20

## References
- https://git.kernel.org/stable/c/06e5b43ca4dab06a92bf4c2f33766e6fb11b880a
- https://git.kernel.org/stable/c/229f47603dd306bc0eb1a831439adb8e48bb0eae
- https://git.kernel.org/stable/c/30d0901b307f27d36b2655fb3048cf31ee0e89c0
- https://git.kernel.org/stable/c/603a47f2ae56bf68288784d3c0a8c5b8e0a827ed
- https://git.kernel.org/stable/c/9629f2dfdb1dad294b468038ff8e161e94d0b609
- https://git.kernel.org/stable/c/a0e44c64b6061dda7e00b7c458e4523e2331b739
- https://git.kernel.org/stable/c/c2a4b5dc8fa71af73bab704d0cac42ac39767ed6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49939.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
