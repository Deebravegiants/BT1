# [C] ksmbd: fix use-after-free by using call_rcu() for oplock_info

## Summary
Severity: Critical
Advisory: CVE-2026-43376
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43376
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.15.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free by using call_rcu() for oplock_info

ksmbd currently frees oplock_info immediately using kfree(), even
though it is accessed under RCU read-side critical sections in places
like opinfo_get() and proc_show_files().

Since there is no RCU grace period delay between nullifying the pointer
and freeing the memory, a reader can still access oplock_info
structure after it has been freed. This can leads to a use-after-free
especially in opinfo_get() where atomic_inc_not_zero() is called on
already freed memory.

Fix this by switching to deferred freeing using call_rcu().

## References
- https://git.kernel.org/stable/c/08aa9f3c8cf4d0bee44df540dfe34e8d64069f2c
- https://git.kernel.org/stable/c/1d6abf145615dbfe267ce3b0a271f95e3780e18e
- https://git.kernel.org/stable/c/1dfd062caa165ec9d7ee0823087930f3ab8a6294
- https://git.kernel.org/stable/c/302fef75512b2c8329a3f5efab1ae7ba2562387a
- https://git.kernel.org/stable/c/ce8507ee82c888126d8e7565e27c016308d24cde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43376.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43376
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
