# [M] drivers: staging: rtl8192u: Fix deadlock in ieee80211_beacons_stop()

## Summary
Severity: Medium
Advisory: CVE-2022-49305
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49305
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: staging: rtl8192u: Fix deadlock in ieee80211_beacons_stop()

There is a deadlock in ieee80211_beacons_stop(), which is shown below:

   (Thread 1)              |      (Thread 2)
                           | ieee80211_send_beacon()
ieee80211_beacons_stop()   |  mod_timer()
 spin_lock_irqsave() //(1) |  (wait a time)
 ...                       | ieee80211_send_beacon_cb()
 del_timer_sync()          |  spin_lock_irqsave() //(2)
 (wait timer to stop)      |  ...

We hold ieee->beacon_lock in position (1) of thread 1 and use
del_timer_sync() to wait timer to stop, but timer handler
also need ieee->beacon_lock in position (2) of thread 2.
As a result, ieee80211_beacons_stop() will block forever.

This patch extracts del_timer_sync() from the protection of
spin_lock_irqsave(), which could let timer handler to obtain
the needed lock.

## References
- https://git.kernel.org/stable/c/042915c1bfedd684c1d98a841794ee203200571a
- https://git.kernel.org/stable/c/1fbe033c52480f7954c057510040fa6286c4ea25
- https://git.kernel.org/stable/c/66f769762f65d957f688f3258755c6ec410bf710
- https://git.kernel.org/stable/c/806c7b53414934ba2a39449b31fd1a038e500273
- https://git.kernel.org/stable/c/b34cb54923a6e5ddefbaf358c85c922c6ab456e2
- https://git.kernel.org/stable/c/b465bb2ebf666116c1ac745cb80c65154dc0d27e
- https://git.kernel.org/stable/c/ffc9cab7243f8151be37966301307bfd3cda2db3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49305.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49305
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
