# [H] ethtool: Avoid overflowing userspace buffer on stats query

## Summary
Severity: High
Advisory: CVE-2025-68795
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68795
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: Avoid overflowing userspace buffer on stats query

The ethtool -S command operates across three ioctl calls:
ETHTOOL_GSSET_INFO for the size, ETHTOOL_GSTRINGS for the names, and
ETHTOOL_GSTATS for the values.

If the number of stats changes between these calls (e.g., due to device
reconfiguration), userspace's buffer allocation will be incorrect,
potentially leading to buffer overflow.

Drivers are generally expected to maintain stable stat counts, but some
drivers (e.g., mlx5, bnx2x, bna, ksz884x) use dynamic counters, making
this scenario possible.

Some drivers try to handle this internally:
- bnad_get_ethtool_stats() returns early in case stats.n_stats is not
  equal to the driver's stats count.
- micrel/ksz884x also makes sure not to write anything beyond
  stats.n_stats and overflow the buffer.

However, both use stats.n_stats which is already assigned with the value
returned from get_sset_count(), hence won't solve the issue described
here.

Change ethtool_get_strings(), ethtool_get_stats(),
ethtool_get_phy_stats() to not return anything in case of a mismatch
between userspace's size and get_sset_size(), to prevent buffer
overflow.
The returned n_stats value will be equal to zero, to reflect that
nothing has been returned.

This could result in one of two cases when using upstream ethtool,
depending on when the size change is detected:
1. When detected in ethtool_get_strings():
    # ethtool -S eth2
    no stats available

2. When detected in get stats, all stats will be reported as zero.

Both cases are presumably transient, and a subsequent ethtool call
should succeed.

Other than the overflow avoidance, these two cases are very evident (no
output/cleared stats), which is arguably better than presenting
incorrect/shifted stats.
I also considered returning an error instead of a "silent" response, but
that seems more destructive towards userspace apps.

Notes:
- This patch does not claim to fix the inherent race, it only makes sure
  that we do not overflow the userspace buffer, and makes for a more
  predictable behavior.

- RTNL lock is held during each ioctl, the race window exists between
  the separate ioctl calls when the lock is released.

- Userspace ethtool always fills stats.n_stats, but it is likely that
  these stats ioctls are implemented in other userspace applications
  which might not fill it. The added code checks that it's not zero,
  to prevent any regressions.

## References
- https://git.kernel.org/stable/c/3df375a1e75483b7d973c3cc2e46aa374db8428b
- https://git.kernel.org/stable/c/4066b5b546293f44cd6d0e84ece6e3ee7ff27093
- https://git.kernel.org/stable/c/4afcb985355210e1688560dc47e64b94dad35d71
- https://git.kernel.org/stable/c/7b07be1ff1cb6c49869910518650e8d0abc7d25f
- https://git.kernel.org/stable/c/7bea09f60f2ad5d232e2db8f1c14e850fd3fd416
- https://git.kernel.org/stable/c/ca9983bc3a1189bd72f9ae449d925a66b2616326
- https://git.kernel.org/stable/c/f9dc0f45d2cd0189ce666288a29d2cc32c2e44d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68795.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68795
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
