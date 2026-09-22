# [M] macsec: sync features on RTM_NEWLINK

## Summary
Severity: Medium
Advisory: CVE-2025-39874
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39874
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

macsec: sync features on RTM_NEWLINK

Syzkaller managed to lock the lower device via ETHTOOL_SFEATURES:

 netdev_lock include/linux/netdevice.h:2761 [inline]
 netdev_lock_ops include/net/netdev_lock.h:42 [inline]
 netdev_sync_lower_features net/core/dev.c:10649 [inline]
 __netdev_update_features+0xcb1/0x1be0 net/core/dev.c:10819
 netdev_update_features+0x6d/0xe0 net/core/dev.c:10876
 macsec_notify+0x2f5/0x660 drivers/net/macsec.c:4533
 notifier_call_chain+0x1b3/0x3e0 kernel/notifier.c:85
 call_netdevice_notifiers_extack net/core/dev.c:2267 [inline]
 call_netdevice_notifiers net/core/dev.c:2281 [inline]
 netdev_features_change+0x85/0xc0 net/core/dev.c:1570
 __dev_ethtool net/ethtool/ioctl.c:3469 [inline]
 dev_ethtool+0x1536/0x19b0 net/ethtool/ioctl.c:3502
 dev_ioctl+0x392/0x1150 net/core/dev_ioctl.c:759

It happens because lower features are out of sync with the upper:

  __dev_ethtool (real_dev)
    netdev_lock_ops(real_dev)
    ETHTOOL_SFEATURES
      __netdev_features_change
        netdev_sync_upper_features
          disable LRO on the lower
    if (old_features != dev->features)
      netdev_features_change
        fires NETDEV_FEAT_CHANGE
	macsec_notify
	  NETDEV_FEAT_CHANGE
	    netdev_update_features (for each macsec dev)
	      netdev_sync_lower_features
	        if (upper_features != lower_features)
	          netdev_lock_ops(lower) # lower == real_dev
		  stuck
		  ...

    netdev_unlock_ops(real_dev)

Per commit af5f54b0ef9e ("net: Lock lower level devices when updating
features"), we elide the lock/unlock when the upper and lower features
are synced. Makes sure the lower (real_dev) has proper features after
the macsec link has been created. This makes sure we never hit the
situation where we need to sync upper flags to the lower.

## References
- https://git.kernel.org/stable/c/0f82c3ba66c6b2e3cde0f255156a753b108ee9dc
- https://git.kernel.org/stable/c/d7624629ccf47135c65fef0701fa0d9a115b87f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39874.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
