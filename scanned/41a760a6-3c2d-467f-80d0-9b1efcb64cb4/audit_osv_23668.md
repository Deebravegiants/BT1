# [M] drivers: staging: rtl8192e: Fix deadlock in rtllib_beacons_stop()

## Summary
Severity: Medium
Advisory: CVE-2022-49315
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49315
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: staging: rtl8192e: Fix deadlock in rtllib_beacons_stop()

There is a deadlock in rtllib_beacons_stop(), which is shown
below:

   (Thread 1)              |      (Thread 2)
                           | rtllib_send_beacon()
rtllib_beacons_stop()      |  mod_timer()
 spin_lock_irqsave() //(1) |  (wait a time)
 ...                       | rtllib_send_beacon_cb()
 del_timer_sync()          |  spin_lock_irqsave() //(2)
 (wait timer to stop)      |  ...

We hold ieee->beacon_lock in position (1) of thread 1 and
use del_timer_sync() to wait timer to stop, but timer handler
also need ieee->beacon_lock in position (2) of thread 2.
As a result, rtllib_beacons_stop() will block forever.

This patch extracts del_timer_sync() from the protection of
spin_lock_irqsave(), which could let timer handler to obtain
the needed lock.

## References
- https://git.kernel.org/stable/c/08bacf871c019163ccd1389d0bc957a43324967a
- https://git.kernel.org/stable/c/0f69d7d5e918aa43423d86bd17ddb11b1b5e8ada
- https://git.kernel.org/stable/c/381045dc64d23a2229c47c5524c06bfc33d34446
- https://git.kernel.org/stable/c/4681129fda9e8555392eaaadb239ec6a6e2b3e12
- https://git.kernel.org/stable/c/46c861009bf437a18417df24cea0d181741b7d72
- https://git.kernel.org/stable/c/64b05fa212c7e4d057676e8b7e7120c6eb2f615b
- https://git.kernel.org/stable/c/9b6bdbd9337de3917945847bde262a34a87a6303
- https://git.kernel.org/stable/c/fef451f0fbbe85dbd2962b18379d02e2965610db
- https://git.kernel.org/stable/c/ffd4c4d5293e4985092ea45ba21cad9326e2e434
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49315.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49315
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
