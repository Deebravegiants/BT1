# [H] s390: fix double free of GS and RI CBs on fork() failure

## Summary
Severity: High
Advisory: CVE-2022-49990
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49990
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.257, >=4.20.0 <5.4.212, >=5.5.0 <5.10.140, >=5.11.0 <5.15.64, >=5.16.0 <5.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390: fix double free of GS and RI CBs on fork() failure

The pointers for guarded storage and runtime instrumentation control
blocks are stored in the thread_struct of the associated task. These
pointers are initially copied on fork() via arch_dup_task_struct()
and then cleared via copy_thread() before fork() returns. If fork()
happens to fail after the initial task dup and before copy_thread(),
the newly allocated task and associated thread_struct memory are
freed via free_task() -> arch_release_task_struct(). This results in
a double free of the guarded storage and runtime info structs
because the fields in the failed task still refer to memory
associated with the source task.

This problem can manifest as a BUG_ON() in set_freepointer() (with
CONFIG_SLAB_FREELIST_HARDENED enabled) or KASAN splat (if enabled)
when running trinity syscall fuzz tests on s390x. To avoid this
problem, clear the associated pointer fields in
arch_dup_task_struct() immediately after the new task is copied.
Note that the RI flag is still cleared in copy_thread() because it
resides in thread stack memory and that is where stack info is
copied.

## References
- https://git.kernel.org/stable/c/13cccafe0edcd03bf1c841de8ab8a1c8e34f77d9
- https://git.kernel.org/stable/c/25a95303b9e513cd2978aacc385d06e6fec23d07
- https://git.kernel.org/stable/c/297ae7e87a87a001dd3dfeac1cb26a42fd929708
- https://git.kernel.org/stable/c/8195e065abf3df84eb0ad2987e76a40f21d1791c
- https://git.kernel.org/stable/c/cacd522e6652fbc2dc0cc6ae11c4e30782fef14b
- https://git.kernel.org/stable/c/fbdc482d43eda40a70de4b0155843d5472f6de62
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49990.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
