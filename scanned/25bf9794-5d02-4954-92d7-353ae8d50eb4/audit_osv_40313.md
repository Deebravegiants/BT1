# [H] fs/fcntl: fix SOFTIRQ-unsafe lock order in fasync signaling

## Summary
Severity: High
Advisory: CVE-2026-52946
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52946
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13, >=7.1.0 <7.1.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/fcntl: fix SOFTIRQ-unsafe lock order in fasync signaling

A SOFTIRQ-safe to SOFTIRQ-unsafe lock order deadlock can occur in
send_sigio() and send_sigurg() when a process group receives a signal.

When FASYNC is configured for a process group (PIDTYPE_PGID), both
functions use read_lock(&tasklist_lock) to traverse the task list.
However, they are frequently called from softirq context:
- send_sigio() via input_inject_event -> kill_fasync
- send_sigurg() via tcp_check_urg -> sk_send_sigurg (NET_RX_SOFTIRQ)

The deadlock is caused by the rwlock writer fairness mechanism:
1. CPU 0 (process context) holds read_lock(&tasklist_lock) in do_wait().
2. CPU 1 (process context) attempts write_lock(&tasklist_lock) in
   fork() or exit() and spins, which blocks all new readers.
3. CPU 0 is interrupted by a softirq (e.g., TCP URG packet reception).
4. The softirq calls send_sigurg() and attempts to acquire
   read_lock(&tasklist_lock), deadlocking because CPU 1 is waiting.

Since PID hashing and do_each_pid_task() traversals are already
RCU-protected, the read_lock on tasklist_lock is no longer strictly
required for safe traversal. Fix this by replacing tasklist_lock with
rcu_read_lock(), aligning the process group signaling path with the
single-PID path. This also mitigates a potential remote denial of
service vector via TCP URG packets.

Lockdep splat:
=====================================================
WARNING: SOFTIRQ-safe -> SOFTIRQ-unsafe lock order detected
[...]
Chain exists of:
  &dev->event_lock --> &f_owner->lock --> tasklist_lock

Possible interrupt unsafe locking scenario:
       CPU0                    CPU1
       ----                    ----
  lock(tasklist_lock);
                           local_irq_disable();
                           lock(&dev->event_lock);
                           lock(&f_owner->lock);
  <Interrupt>
    lock(&dev->event_lock);

*** DEADLOCK ***

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/00633c4683828acd5256fa8d5163f440d74bbe71
- https://git.kernel.org/stable/c/1bee417678f1135e35b25a37734db46aa94258d2
- https://git.kernel.org/stable/c/20a93e397abe850c49b6fa0e8cc827b5f634a8f5
- https://git.kernel.org/stable/c/32dbd5ce4be3a3ed7e00f8af18795cc84fc50a33
- https://git.kernel.org/stable/c/36c1b57b2ecf3c61ac93f5f07bd29b6f21e226ed
- https://git.kernel.org/stable/c/54626335ea4174ab2d9a183b511d825f6765e47b
- https://git.kernel.org/stable/c/897d6a7247739fb1528f98c575df4f2e5de7f994
- https://git.kernel.org/stable/c/b5fa9e32fb6718f70c986ee14dd5d01b4846f331
- https://git.kernel.org/stable/c/bfcc8e8d8a495bb34cae9e620adfb75fb13a3954
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52946.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52946
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
