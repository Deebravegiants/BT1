# [H] sched/ext: Fix invalid task state transitions on class switch

## Summary
Severity: High
Advisory: CVE-2025-39780
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39780
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/ext: Fix invalid task state transitions on class switch

When enabling a sched_ext scheduler, we may trigger invalid task state
transitions, resulting in warnings like the following (which can be
easily reproduced by running the hotplug selftest in a loop):

 sched_ext: Invalid task state transition 0 -> 3 for fish[770]
 WARNING: CPU: 18 PID: 787 at kernel/sched/ext.c:3862 scx_set_task_state+0x7c/0xc0
 ...
 RIP: 0010:scx_set_task_state+0x7c/0xc0
 ...
 Call Trace:
  <TASK>
  scx_enable_task+0x11f/0x2e0
  switching_to_scx+0x24/0x110
  scx_enable.isra.0+0xd14/0x13d0
  bpf_struct_ops_link_create+0x136/0x1a0
  __sys_bpf+0x1edd/0x2c30
  __x64_sys_bpf+0x21/0x30
  do_syscall_64+0xbb/0x370
  entry_SYSCALL_64_after_hwframe+0x77/0x7f

This happens because we skip initialization for tasks that are already
dead (with their usage counter set to zero), but we don't exclude them
during the scheduling class transition phase.

Fix this by also skipping dead tasks during class swiching, preventing
invalid task state transitions.

## References
- https://git.kernel.org/stable/c/6a32cbe95029ebe21cc08349fd7ef2a3d32d2043
- https://git.kernel.org/stable/c/786f6314604b34c3e7de5f733f4e08e35c448a50
- https://git.kernel.org/stable/c/ddf7233fcab6c247379d0928d46cc316ee122229
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39780.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39780
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
