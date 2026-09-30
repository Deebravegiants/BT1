# [M] drivers: usb: host: Fix deadlock in oxu_bus_suspend()

## Summary
Severity: Medium
Advisory: CVE-2022-49313
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49313
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: usb: host: Fix deadlock in oxu_bus_suspend()

There is a deadlock in oxu_bus_suspend(), which is shown below:

   (Thread 1)              |      (Thread 2)
                           | timer_action()
oxu_bus_suspend()          |  mod_timer()
 spin_lock_irq() //(1)     |  (wait a time)
 ...                       | oxu_watchdog()
 del_timer_sync()          |  spin_lock_irq() //(2)
 (wait timer to stop)      |  ...

We hold oxu->lock in position (1) of thread 1, and use
del_timer_sync() to wait timer to stop, but timer handler
also need oxu->lock in position (2) of thread 2. As a result,
oxu_bus_suspend() will block forever.

This patch extracts del_timer_sync() from the protection of
spin_lock_irq(), which could let timer handler to obtain
the needed lock.

## References
- https://git.kernel.org/stable/c/2dcec0bc142be2096af71a5703d63237127db204
- https://git.kernel.org/stable/c/4187b291a76664a3c03d3f0d9bfadc8322881868
- https://git.kernel.org/stable/c/4d378f2ae58138d4c55684e1d274e7dd94aa6524
- https://git.kernel.org/stable/c/9b58d255f27b0ed6a2e43208960864d67579db58
- https://git.kernel.org/stable/c/a3d380188bde8900c3f604e82b56572896499124
- https://git.kernel.org/stable/c/b97aae8b43b718314012e8170b7e03dbfd2e7677
- https://git.kernel.org/stable/c/d888753872190abd18f68a7d77b9c7c367f0a7ab
- https://git.kernel.org/stable/c/f8242044c91cafbba9e320b0fb31abf2429a3221
- https://git.kernel.org/stable/c/ffe9440d698274c6462d2e304562c6ddfc8c84df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49313.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49313
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
