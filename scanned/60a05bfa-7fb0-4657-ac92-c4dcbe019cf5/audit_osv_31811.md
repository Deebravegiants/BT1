# [H] batman-adv: Drop unmanaged ELP metric worker

## Summary
Severity: High
Advisory: CVE-2025-21823
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21823
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: Drop unmanaged ELP metric worker

The ELP worker needs to calculate new metric values for all neighbors
"reachable" over an interface. Some of the used metric sources require
locks which might need to sleep. This sleep is incompatible with the RCU
list iterator used for the recorded neighbors. The initial approach to work
around of this problem was to queue another work item per neighbor and then
run this in a new context.

Even when this solved the RCU vs might_sleep() conflict, it has a major
problems: Nothing was stopping the work item in case it is not needed
anymore - for example because one of the related interfaces was removed or
the batman-adv module was unloaded - resulting in potential invalid memory
accesses.

Directly canceling the metric worker also has various problems:

* cancel_work_sync for a to-be-deactivated interface is called with
  rtnl_lock held. But the code in the ELP metric worker also tries to use
  rtnl_lock() - which will never return in this case. This also means that
  cancel_work_sync would never return because it is waiting for the worker
  to finish.
* iterating over the neighbor list for the to-be-deactivated interface is
  currently done using the RCU specific methods. Which means that it is
  possible to miss items when iterating over it without the associated
  spinlock - a behaviour which is acceptable for a periodic metric check
  but not for a cleanup routine (which must "stop" all still running
  workers)

The better approch is to get rid of the per interface neighbor metric
worker and handle everything in the interface worker. The original problems
are solved by:

* creating a list of neighbors which require new metric information inside
  the RCU protected context, gathering the metric according to the new list
  outside the RCU protected context
* only use rcu_trylock inside metric gathering code to avoid a deadlock
  when the cancel_delayed_work_sync is called in the interface removal code
  (which is called with the rtnl_lock held)

## References
- https://git.kernel.org/stable/c/0fdc3c166ac17b26014313fa2b93696354511b24
- https://git.kernel.org/stable/c/1c334629176c2d644befc31a20d4bf75542f7631
- https://git.kernel.org/stable/c/3c0e0aecb78cb2a2ca1dc701982d08fedb088dc6
- https://git.kernel.org/stable/c/781a06fd265a8151f7601122d9c2e985663828ff
- https://git.kernel.org/stable/c/8c8ecc98f5c65947b0070a24bac11e12e47cc65d
- https://git.kernel.org/stable/c/a0019971f340ae02ba54cf1861f72da7e03e6b66
- https://git.kernel.org/stable/c/a7aa2317285806640c844acd4cd2cd768e395264
- https://git.kernel.org/stable/c/af264c2a9adc37f4bdf88ca7f3affa15d8c7de9e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21823.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
