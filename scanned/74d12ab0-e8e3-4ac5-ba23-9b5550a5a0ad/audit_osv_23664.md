# [M] drivers: staging: rtl8192bs: Fix deadlock in rtw_joinbss_event_prehandle()

## Summary
Severity: Medium
Advisory: CVE-2022-49311
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49311
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: staging: rtl8192bs: Fix deadlock in rtw_joinbss_event_prehandle()

There is a deadlock in rtw_joinbss_event_prehandle(), which is shown
below:

   (Thread 1)                |      (Thread 2)
                             | _set_timer()
rtw_joinbss_event_prehandle()|  mod_timer()
 spin_lock_bh() //(1)        |  (wait a time)
 ...                         | _rtw_join_timeout_handler()
 del_timer_sync()            |  spin_lock_bh() //(2)
 (wait timer to stop)        |  ...

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
- https://git.kernel.org/stable/c/041879b12ddb0c6c83ed9c0bdd10dc82a056f2fc
- https://git.kernel.org/stable/c/1f6c99b94ca3caad346876b3e22e3ca3d25bc8ee
- https://git.kernel.org/stable/c/ae60744d5fad840b9d056d35b4b652d95e755846
- https://git.kernel.org/stable/c/eca9748d9267a38d532464e3305a38629e9c35a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49311.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49311
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
