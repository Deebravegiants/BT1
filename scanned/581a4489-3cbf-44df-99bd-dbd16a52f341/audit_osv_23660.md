# [M] drivers: tty: serial: Fix deadlock in sa1100_set_termios()

## Summary
Severity: Medium
Advisory: CVE-2022-49304
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49304
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: tty: serial: Fix deadlock in sa1100_set_termios()

There is a deadlock in sa1100_set_termios(), which is shown
below:

   (Thread 1)              |      (Thread 2)
                           | sa1100_enable_ms()
sa1100_set_termios()       |  mod_timer()
 spin_lock_irqsave() //(1) |  (wait a time)
 ...                       | sa1100_timeout()
 del_timer_sync()          |  spin_lock_irqsave() //(2)
 (wait timer to stop)      |  ...

We hold sport->port.lock in position (1) of thread 1 and
use del_timer_sync() to wait timer to stop, but timer handler
also need sport->port.lock in position (2) of thread 2. As a result,
sa1100_set_termios() will block forever.

This patch moves del_timer_sync() before spin_lock_irqsave()
in order to prevent the deadlock.

## References
- https://git.kernel.org/stable/c/0976808d0d171ec837d4bd3e9f4ad4a00ab703b8
- https://git.kernel.org/stable/c/09a5958a2452ad22d0cb638711ef34ea1863a829
- https://git.kernel.org/stable/c/2cbfc38df580bff5b2fe19f21c1a7520efcc4b3b
- https://git.kernel.org/stable/c/34d91e555e5582cffdbcbb75517bc9217866823e
- https://git.kernel.org/stable/c/553213432ef0c295becdc08c0207d2094468f673
- https://git.kernel.org/stable/c/62b2caef400c1738b6d22f636c628d9f85cd4c4c
- https://git.kernel.org/stable/c/6e2273eefab54a521d9c59efb6e1114e742bdf41
- https://git.kernel.org/stable/c/85e20f8bd31a46d8c60103d0274a8ebe8f47f2b2
- https://git.kernel.org/stable/c/920f0ae7a129ffee98a106e3bbdfd61a2a59e939
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49304.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
