# [M] net: phy: transfer phy_config_inband() locking responsibility to phylink

## Summary
Severity: Medium
Advisory: CVE-2025-39915
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39915
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: transfer phy_config_inband() locking responsibility to phylink

Problem description
===================

Lockdep reports a possible circular locking dependency (AB/BA) between
&pl->state_mutex and &phy->lock, as follows.

phylink_resolve() // acquires &pl->state_mutex
-> phylink_major_config()
   -> phy_config_inband() // acquires &pl->phydev->lock

whereas all the other call sites where &pl->state_mutex and
&pl->phydev->lock have the locking scheme reversed. Everywhere else,
&pl->phydev->lock is acquired at the top level, and &pl->state_mutex at
the lower level. A clear example is phylink_bringup_phy().

The outlier is the newly introduced phy_config_inband() and the existing
lock order is the correct one. To understand why it cannot be the other
way around, it is sufficient to consider phylink_phy_change(), phylink's
callback from the PHY device's phy->phy_link_change() virtual method,
invoked by the PHY state machine.

phy_link_up() and phy_link_down(), the (indirect) callers of
phylink_phy_change(), are called with &phydev->lock acquired.
Then phylink_phy_change() acquires its own &pl->state_mutex, to
serialize changes made to its pl->phy_state and pl->link_config.
So all other instances of &pl->state_mutex and &phydev->lock must be
consistent with this order.

Problem impact
==============

I think the kernel runs a serious deadlock risk if an existing
phylink_resolve() thread, which results in a phy_config_inband() call,
is concurrent with a phy_link_up() or phy_link_down() call, which will
deadlock on &pl->state_mutex in phylink_phy_change(). Practically
speaking, the impact may be limited by the slow speed of the medium
auto-negotiation protocol, which makes it unlikely for the current state
to still be unresolved when a new one is detected, but I think the
problem is there. Nonetheless, the problem was discovered using lockdep.

Proposed solution
=================

Practically speaking, the phy_config_inband() requirement of having
phydev->lock acquired must transfer to the caller (phylink is the only
caller). There, it must bubble up until immediately before
&pl->state_mutex is acquired, for the cases where that takes place.

Solution details, considerations, notes
=======================================

This is the phy_config_inband() call graph:

                          sfp_upstream_ops :: connect_phy()
                          |
                          v
                          phylink_sfp_connect_phy()
                          |
                          v
                          phylink_sfp_config_phy()
                          |
                          |   sfp_upstream_ops :: module_insert()
                          |   |
                          |   v
                          |   phylink_sfp_module_insert()
                          |   |
                          |   |   sfp_upstream_ops :: module_start()
                          |   |   |
                          |   |   v
                          |   |   phylink_sfp_module_start()
                          |   |   |
                          |   v   v
                          |   phylink_sfp_config_optical()
 phylink_start()          |   |
   |   phylink_resume()   v   v
   |   |  phylink_sfp_set_config()
   |   |  |
   v   v  v
 phylink_mac_initial_config()
   |   phylink_resolve()
   |   |  phylink_ethtool_ksettings_set()
   v   v  v
   phylink_major_config()
            |
            v
    phy_config_inband()

phylink_major_config() caller #1, phylink_mac_initial_config(), does not
acquire &pl->state_mutex nor do its callers. It must acquire
&pl->phydev->lock prior to calling phylink_major_config().

phylink_major_config() caller #2, phylink_resolve() acquires
&pl->state_mutex, thus also needs to acquire &pl->phydev->lock.

phylink_major_config() caller #3, phylink_ethtool_ksettings_set(), is
completely uninteresting, because it only call
---truncated---

## References
- https://git.kernel.org/stable/c/052ac41c379c8b87629808be612a482b2d0ae283
- https://git.kernel.org/stable/c/e2a10daba84968f6b5777d150985fd7d6abc9c84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39915.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39915
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
