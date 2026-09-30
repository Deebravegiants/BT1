# [C] mptcp: fix race condition in mptcp_schedule_work()

## Summary
Severity: Critical
Advisory: CVE-2025-40258
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40258
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.118, >=6.7.0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix race condition in mptcp_schedule_work()

syzbot reported use-after-free in mptcp_schedule_work() [1]

Issue here is that mptcp_schedule_work() schedules a work,
then gets a refcount on sk->sk_refcnt if the work was scheduled.
This refcount will be released by mptcp_worker().

[A] if (schedule_work(...)) {
[B]     sock_hold(sk);
        return true;
    }

Problem is that mptcp_worker() can run immediately and complete before [B]

We need instead :

    sock_hold(sk);
    if (schedule_work(...))
        return true;
    sock_put(sk);

[1]
refcount_t: addition on 0; use-after-free.
 WARNING: CPU: 1 PID: 29 at lib/refcount.c:25 refcount_warn_saturate+0xfa/0x1d0 lib/refcount.c:25
Call Trace:
 <TASK>
 __refcount_add include/linux/refcount.h:-1 [inline]
  __refcount_inc include/linux/refcount.h:366 [inline]
  refcount_inc include/linux/refcount.h:383 [inline]
  sock_hold include/net/sock.h:816 [inline]
  mptcp_schedule_work+0x164/0x1a0 net/mptcp/protocol.c:943
  mptcp_tout_timer+0x21/0xa0 net/mptcp/protocol.c:2316
  call_timer_fn+0x17e/0x5f0 kernel/time/timer.c:1747
  expire_timers kernel/time/timer.c:1798 [inline]
  __run_timers kernel/time/timer.c:2372 [inline]
  __run_timer_base+0x648/0x970 kernel/time/timer.c:2384
  run_timer_base kernel/time/timer.c:2393 [inline]
  run_timer_softirq+0xb7/0x180 kernel/time/timer.c:2403
  handle_softirqs+0x22f/0x710 kernel/softirq.c:622
  __do_softirq kernel/softirq.c:656 [inline]
  run_ktimerd+0xcf/0x190 kernel/softirq.c:1138
  smpboot_thread_fn+0x542/0xa60 kernel/smpboot.c:160
  kthread+0x711/0x8a0 kernel/kthread.c:463
  ret_from_fork+0x4bc/0x870 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/035bca3f017ee9dea3a5a756e77a6f7138cc6eea
- https://git.kernel.org/stable/c/3fc7723ed01d1130d4bf7063c50e0af60ecccbb4
- https://git.kernel.org/stable/c/8f9ba1a99a89feef9b5867c15a0141a97e893309
- https://git.kernel.org/stable/c/99908e2d601236842d705d5fd04fb349577316f5
- https://git.kernel.org/stable/c/ac28dfddedf6f209190950fc71bcff65ec4ab47b
- https://git.kernel.org/stable/c/db4f7968a75250ca6c4ed70d0a78beabb2dcee18
- https://git.kernel.org/stable/c/f865e6595acf33083168db76921e66ace8bf0e5b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40258.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
