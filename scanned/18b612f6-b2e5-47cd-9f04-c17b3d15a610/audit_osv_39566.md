# [H] exit: prevent preemption of oopsing TASK_DEAD task

## Summary
Severity: High
Advisory: CVE-2026-46173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46173
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

exit: prevent preemption of oopsing TASK_DEAD task

When an already-exiting task oopses, make_task_dead() currently calls
do_task_dead() with preemption enabled.  That is forbidden:
do_task_dead() calls __schedule(), which has a comment saying "WARNING:
must be called with preemption disabled!".

If an oopsing task is preempted in do_task_dead(), between becoming
TASK_DEAD and entering the scheduler explicitly, bad things happen:
finish_task_switch() assumes that once the scheduler has switched away
from a TASK_DEAD task, the task can never run again and its stack is no
longer needed; but that assumption apparently doesn't hold if the dead
task was preempted (the SM_PREEMPT case).

This means that the scheduler ends up repeatedly dropping references on
the dead task's stack, which can lead to use-after-free or double-free
of the entire task stack; in other words, two tasks can end up running
on the same stack, resulting in various kinds of memory corruption.

(This does not just affect "recursively oopsing" tasks; it is enough to
oops once during task exit, for example in a file_operations::release
handler)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/3d6fb8a7690c23e3213c4b008f64d89a44b98737
- https://git.kernel.org/stable/c/640b4c00fb0e2920327435f6176cbefc3c546165
- https://git.kernel.org/stable/c/6f49f94f3b11fe8bff1bf2a054143789e76aaf17
- https://git.kernel.org/stable/c/7b2800ba5f5f77a8ee7f4cbadb19cf1264597a34
- https://git.kernel.org/stable/c/9756b3db5db6c2f5eccb32dddbd88eb4c54f575e
- https://git.kernel.org/stable/c/c1fa0bb633e4a6b11e83ffc57fa5abe8ebb87891
- https://project-zero.issues.chromium.org/issues/510793286
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46173.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
