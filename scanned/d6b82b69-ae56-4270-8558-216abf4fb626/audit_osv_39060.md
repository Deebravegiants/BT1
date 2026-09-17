# [H] rtmutex: Use waiter::task instead of current in remove_waiter()

## Summary
Severity: High
Advisory: CVE-2026-43499
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43499
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtmutex: Use waiter::task instead of current in remove_waiter()

remove_waiter() is used by the slowlock paths, but it is also used for
proxy-lock rollback in rt_mutex_start_proxy_lock() when invoked from
futex_requeue().

In the latter case waiter::task is not current, but remove_waiter()
operates on current for the dequeue operation. That results in several
problems:

  1) the rbtree dequeue happens without waiter::task::pi_lock being held

  2) the waiter task's pi_blocked_on state is not cleared, which leaves a
     dangling pointer primed for UAF around.

  3) rt_mutex_adjust_prio_chain() operates on the wrong top priority waiter
     task

Use waiter::task instead of current in all related operations in
remove_waiter() to cure those problems.

[ tglx: Fixup rt_mutex_adjust_prio_chain(), add a comment and amend the
  	changelog ]

## References
- http://www.openwall.com/lists/oss-security/2026/07/08/12
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/3bfdc63936dd4773109b7b8c280c0f3b5ae7d349
- https://git.kernel.org/stable/c/3fb7394a837740770f0d6b4b30567e60786a63f2
- https://git.kernel.org/stable/c/6d52dfcb2a5db86e346cf51f8fcf2071b8085166
- https://git.kernel.org/stable/c/838ce5cb5d93c3ab8b27e75bc6ad905a94b752fd
- https://git.kernel.org/stable/c/88614876370aac8ad1050ad785a4c095ba17ac11
- https://git.kernel.org/stable/c/8a1fc8d698ac5e5916e3082a0f74450d71f9611f
- https://git.kernel.org/stable/c/d8cce4773c2b23d819baf5abedc62f7b430e8745
- https://git.kernel.org/stable/c/f3fa3424bceb128d2be4b3745506b22844b87db7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43499.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43499
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
