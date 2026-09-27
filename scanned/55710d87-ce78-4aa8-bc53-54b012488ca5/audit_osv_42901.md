# [H] can: bcm: defer rx_op deallocation to workqueue to fix thrtimer UAF

## Summary
Severity: High
Advisory: CVE-2026-72123
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72123
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.178, >=5.19.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: defer rx_op deallocation to workqueue to fix thrtimer UAF

Commit f1b4e32aca08 ("can: bcm: use call_rcu() instead of costly
synchronize_rcu()") replaced synchronize_rcu() in bcm_delete_rx_op()
with call_rcu() and introduced the RX_NO_AUTOTIMER flag.

However, this flag check was omitted for thrtimer in the packet rx
fast-path. During BCM RX operation teardown, a concurrent RCU reader
(bcm_rx_handler) can race and re-arm thrtimer via
bcm_rx_update_and_send() after call_rcu() has been scheduled.  Once
the RCU grace period elapses, bcm_op is freed.  The subsequently
firing thrtimer then dereferences the deallocated op, causing a UAF.

Adding flag checks to the rx fast-path (bcm_rx_update_and_send) does not
fully close the TOCTOU race and introduces latency for every CAN frame.
Conversely, calling hrtimer_cancel() directly inside the RCU callback
(softirq context) is fatal as hrtimer_cancel() can sleep, triggering
a "scheduling while atomic" panic.

Resolve this by deferring the timer cancellation and memory free to a
dedicated unbound workqueue (bcm_wq).  The RCU callback now queues a
work item to bcm_wq, which safely cancels both timers and deallocates
memory in sleepable process context.  A dedicated workqueue is used to
prevent system-wide WQ saturation and is cleanly flushed/destroyed
on module unload to avoid rmmod page faults.

Since the deferred work can now outlive the calling context by an
unbounded amount, also take a reference on op->sk when it is assigned
and drop it only once the deferred work has cancelled both timers, so a
socket can no longer be freed out from under a still-armed timer whose
callback (bcm_send_to_user()) dereferences op->sk.

## References
- https://git.kernel.org/stable/c/036a8c320ca11bc912e8027adcfad14b326f067e
- https://git.kernel.org/stable/c/3cf4fd5316f449811d8baf1bc6978ef5a7b743a9
- https://git.kernel.org/stable/c/4177762f70646ac48a2af382e45a795cbd295198
- https://git.kernel.org/stable/c/68973f9db76144825e4f35dfdc80fb8279eb2d57
- https://git.kernel.org/stable/c/6fd08e8d826c3aa4cc7021f5f9cdbb7fa7441d3f
- https://git.kernel.org/stable/c/cd830e0bc25ee2d38cbfbdbb3cd77c5f53b2b6d5
- https://git.kernel.org/stable/c/ce2d4b121fb7545e1ed588e860c8e5fd5ad45224
- https://git.kernel.org/stable/c/de5fce46637de05bef56ec08528127676eb6fc9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72123.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
