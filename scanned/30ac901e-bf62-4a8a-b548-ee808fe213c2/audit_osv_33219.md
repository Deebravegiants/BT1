# [H] net: phylink: add lock for serializing concurrent pl->phydev writes with resolver

## Summary
Severity: High
Advisory: CVE-2025-39905
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39905
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phylink: add lock for serializing concurrent pl->phydev writes with resolver

Currently phylink_resolve() protects itself against concurrent
phylink_bringup_phy() or phylink_disconnect_phy() calls which modify
pl->phydev by relying on pl->state_mutex.

The problem is that in phylink_resolve(), pl->state_mutex is in a lock
inversion state with pl->phydev->lock. So pl->phydev->lock needs to be
acquired prior to pl->state_mutex. But that requires dereferencing
pl->phydev in the first place, and without pl->state_mutex, that is
racy.

Hence the reason for the extra lock. Currently it is redundant, but it
will serve a functional purpose once mutex_lock(&phy->lock) will be
moved outside of the mutex_lock(&pl->state_mutex) section.

Another alternative considered would have been to let phylink_resolve()
acquire the rtnl_mutex, which is also held when phylink_bringup_phy()
and phylink_disconnect_phy() are called. But since phylink_disconnect_phy()
runs under rtnl_lock(), it would deadlock with phylink_resolve() when
calling flush_work(&pl->resolve). Additionally, it would have been
undesirable because it would have unnecessarily blocked many other call
paths as well in the entire kernel, so the smaller-scoped lock was
preferred.

## References
- https://git.kernel.org/stable/c/0ba5b2f2c381dbec9ed9e4ab3ae5d3e667de0dc3
- https://git.kernel.org/stable/c/56fe63b05ec84ae6674269d78397cec43a7a295a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39905.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39905
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
