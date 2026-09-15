# [M] drivers: staging: rtl8192eu: Fix deadlock in rtw_joinbss_event_prehandle

## Summary
Severity: Medium
Advisory: CVE-2022-49303
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49303
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: staging: rtl8192eu: Fix deadlock in rtw_joinbss_event_prehandle

There is a deadlock in rtw_joinbss_event_prehandle(), which is shown below:

   (Thread 1)                |      (Thread 2)
                             | _set_timer()
rtw_joinbss_event_prehandle()|  mod_timer()
 spin_lock_bh() //(1)        |  (wait a time)
 ...                         | rtw_join_timeout_handler()
                             |  _rtw_join_timeout_handler()
 del_timer_sync()            |   spin_lock_bh() //(2)
 (wait timer to stop)        |   ...

We hold pmlmepriv->lock in position (1) of thread 1 and
use del_timer_sync() to wait timer to stop, but timer handler
also need pmlmepriv->lock in position (2) of thread 2.
As a result, rtw_joinbss_event_prehandle() will block forever.

This patch extracts del_timer_sync() from the protection of
spin_lock_bh(), which could let timer handler to obtain
the needed lock. What`s more, we change spin_lock_bh() to
spin_lock_irq() in _rtw_join_timeout_handler() in order to
prevent deadlock.

## References
- https://git.kernel.org/stable/c/0fcddf9c7c10202946d5b19409efbdff744fba88
- https://git.kernel.org/stable/c/25cf414b0610fea29d8e045f315648d9007c9a46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49303.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
