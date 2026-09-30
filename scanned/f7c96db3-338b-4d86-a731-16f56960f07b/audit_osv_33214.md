# [M] net_sched: gen_estimator: fix est_timer() vs CONFIG_PREEMPT_RT=y

## Summary
Severity: Medium
Advisory: CVE-2025-39900
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39900
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: gen_estimator: fix est_timer() vs CONFIG_PREEMPT_RT=y

syzbot reported a WARNING in est_timer() [1]

Problem here is that with CONFIG_PREEMPT_RT=y, timer callbacks
can be preempted.

Adopt preempt_disable_nested()/preempt_enable_nested() to fix this.

[1]
 WARNING: CPU: 0 PID: 16 at ./include/linux/seqlock.h:221 __seqprop_assert include/linux/seqlock.h:221 [inline]
 WARNING: CPU: 0 PID: 16 at ./include/linux/seqlock.h:221 est_timer+0x6dc/0x9f0 net/core/gen_estimator.c:93
Modules linked in:
CPU: 0 UID: 0 PID: 16 Comm: ktimers/0 Not tainted syzkaller #0 PREEMPT_{RT,(full)}
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 07/12/2025
 RIP: 0010:__seqprop_assert include/linux/seqlock.h:221 [inline]
 RIP: 0010:est_timer+0x6dc/0x9f0 net/core/gen_estimator.c:93
Call Trace:
 <TASK>
  call_timer_fn+0x17e/0x5f0 kernel/time/timer.c:1747
  expire_timers kernel/time/timer.c:1798 [inline]
  __run_timers kernel/time/timer.c:2372 [inline]
  __run_timer_base+0x648/0x970 kernel/time/timer.c:2384
  run_timer_base kernel/time/timer.c:2393 [inline]
  run_timer_softirq+0xb7/0x180 kernel/time/timer.c:2403
  handle_softirqs+0x22c/0x710 kernel/softirq.c:579
  __do_softirq kernel/softirq.c:613 [inline]
  run_ktimerd+0xcf/0x190 kernel/softirq.c:1043
  smpboot_thread_fn+0x53f/0xa60 kernel/smpboot.c:160
  kthread+0x70e/0x8a0 kernel/kthread.c:463
  ret_from_fork+0x3fc/0x770 arch/x86/kernel/process.c:148
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245
 </TASK>

## References
- https://git.kernel.org/stable/c/9f74c0ea9b26d1505d55b61e36b1623dd347e1d1
- https://git.kernel.org/stable/c/a22ec2ee824be30803068a52f78f7ffe3bc879fb
- https://git.kernel.org/stable/c/e79923824c48b930609680be04cb29253fc4a17d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39900.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39900
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
