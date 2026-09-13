# [H] net: Fix rcu_tasks stall in threaded busypoll

## Summary
Severity: High
Advisory: CVE-2026-43385
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43385
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: Fix rcu_tasks stall in threaded busypoll

I was debugging a NIC driver when I noticed that when I enable
threaded busypoll, bpftrace hangs when starting up. dmesg showed:

  rcu_tasks_wait_gp: rcu_tasks grace period number 85 (since boot) is 10658 jiffies old.
  rcu_tasks_wait_gp: rcu_tasks grace period number 85 (since boot) is 40793 jiffies old.
  rcu_tasks_wait_gp: rcu_tasks grace period number 85 (since boot) is 131273 jiffies old.
  rcu_tasks_wait_gp: rcu_tasks grace period number 85 (since boot) is 402058 jiffies old.
  INFO: rcu_tasks detected stalls on tasks:
  00000000769f52cd: .N nvcsw: 2/2 holdout: 1 idle_cpu: -1/64
  task:napi/eth2-8265  state:R  running task     stack:0     pid:48300 tgid:48300 ppid:2      task_flags:0x208040 flags:0x00004000
  Call Trace:
   <TASK>
   ? napi_threaded_poll_loop+0x27c/0x2c0
   ? __pfx_napi_threaded_poll+0x10/0x10
   ? napi_threaded_poll+0x26/0x80
   ? kthread+0xfa/0x240
   ? __pfx_kthread+0x10/0x10
   ? ret_from_fork+0x31/0x50
   ? __pfx_kthread+0x10/0x10
   ? ret_from_fork_asm+0x1a/0x30
   </TASK>

The cause is that in threaded busypoll, the main loop is in
napi_threaded_poll rather than napi_threaded_poll_loop, where the
latter rarely iterates more than once within its loop. For
rcu_softirq_qs_periodic inside napi_threaded_poll_loop to report its
qs state, the last_qs must be 100ms behind, and this can't happen
because napi_threaded_poll_loop rarely iterates in threaded busypoll,
and each time napi_threaded_poll_loop is called last_qs is reset to
latest jiffies.

This patch changes so that in threaded busypoll, last_qs is saved
in the outer napi_threaded_poll, and whether busy_poll_last_qs
is NULL indicates whether napi_threaded_poll_loop is called for
busypoll. This way last_qs would not reset to latest jiffies on
each invocation of napi_threaded_poll_loop.

## References
- https://git.kernel.org/stable/c/1a86a1f7d88996085934139fa4c063b6299a2dd3
- https://git.kernel.org/stable/c/52459201d0df3fdbb1d281738b7b772e2cacb49c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43385.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
