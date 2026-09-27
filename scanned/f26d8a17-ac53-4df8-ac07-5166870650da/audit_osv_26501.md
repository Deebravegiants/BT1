# [M] drivers: staging: rtl8723bs: Fix locking in _rtw_join_timeout_handler()

## Summary
Severity: Medium
Advisory: CVE-2023-53281
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53281
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.111, >=5.16.0 <6.1.28, >=5.19.0 <6.2.15, >=6.2.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: staging: rtl8723bs: Fix locking in _rtw_join_timeout_handler()

Commit 041879b12ddb ("drivers: staging: rtl8192bs: Fix deadlock in
rtw_joinbss_event_prehandle()") besides fixing the deadlock also
modified _rtw_join_timeout_handler() to use spin_[un]lock_irq()
instead of spin_[un]lock_bh().

_rtw_join_timeout_handler() calls rtw_do_join() which takes
pmlmepriv->scanned_queue.lock using spin_[un]lock_bh(). This
spin_unlock_bh() call re-enables softirqs which triggers an oops in
kernel/softirq.c: __local_bh_enable_ip() when it calls
lockdep_assert_irqs_enabled():

[  244.506087] WARNING: CPU: 2 PID: 0 at kernel/softirq.c:376 __local_bh_enable_ip+0xa6/0x100
...
[  244.509022] Call Trace:
[  244.509048]  <IRQ>
[  244.509100]  _rtw_join_timeout_handler+0x134/0x170 [r8723bs]
[  244.509468]  ? __pfx__rtw_join_timeout_handler+0x10/0x10 [r8723bs]
[  244.509772]  ? __pfx__rtw_join_timeout_handler+0x10/0x10 [r8723bs]
[  244.510076]  call_timer_fn+0x95/0x2a0
[  244.510200]  __run_timers.part.0+0x1da/0x2d0

This oops is causd by the switch to spin_[un]lock_irq() which disables
the IRQs for the entire duration of _rtw_join_timeout_handler().

Disabling the IRQs is not necessary since all code taking this lock
runs from either user contexts or from softirqs, switch back to
spin_[un]lock_bh() to fix this.

## References
- https://git.kernel.org/stable/c/209850f17717a3b5cc558578bef5631ac7045539
- https://git.kernel.org/stable/c/215792eda008f6a1e7ed9d77fa20d582d22bb114
- https://git.kernel.org/stable/c/2a50e44a66d268ee5db3d177f1fdc1503dbce6e7
- https://git.kernel.org/stable/c/4ab1bace1dd3875371b481ef4301c4671bddea22
- https://git.kernel.org/stable/c/dc327e87c6d9bfd9ee08e76396b3c0ba848ec554
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53281.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53281
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
