# [H] Bluetooth: Fix race condition in hidp_session_thread

## Summary
Severity: High
Advisory: CVE-2023-54120
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54120
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.313, >=4.15.0 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.108, >=5.16.0 <6.1.25, >=6.2.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Fix race condition in hidp_session_thread

There is a potential race condition in hidp_session_thread that may
lead to use-after-free. For instance, the timer is active while
hidp_del_timer is called in hidp_session_thread(). After hidp_session_put,
then 'session' will be freed, causing kernel panic when hidp_idle_timeout
is running.

The solution is to use del_timer_sync instead of del_timer.

Here is the call trace:

? hidp_session_probe+0x780/0x780
call_timer_fn+0x2d/0x1e0
__run_timers.part.0+0x569/0x940
hidp_session_probe+0x780/0x780
call_timer_fn+0x1e0/0x1e0
ktime_get+0x5c/0xf0
lapic_next_deadline+0x2c/0x40
clockevents_program_event+0x205/0x320
run_timer_softirq+0xa9/0x1b0
__do_softirq+0x1b9/0x641
__irq_exit_rcu+0xdc/0x190
irq_exit_rcu+0xe/0x20
sysvec_apic_timer_interrupt+0xa1/0xc0

## References
- https://git.kernel.org/stable/c/0efb276d5848a3accc37c6f41b85e442c4768169
- https://git.kernel.org/stable/c/152f47bd6b995e0e98c85672f6d19894bc287ef2
- https://git.kernel.org/stable/c/248af9feca062a4ca9c3f2ccf67056c8a5eb817f
- https://git.kernel.org/stable/c/5f3d214d19899183d4e0cce7552998262112e4ab
- https://git.kernel.org/stable/c/8a99e6200c38b78a45dcd12a6bdc43fdf4dc36be
- https://git.kernel.org/stable/c/c95930abd687fcd1aa040dc4fe90dff947916460
- https://git.kernel.org/stable/c/f6719fd8f409fa1da8dc956e93822d25e1e8b360
- https://git.kernel.org/stable/c/f7ec5ca433ceead8d9d78fd2febff094f289441d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54120.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
