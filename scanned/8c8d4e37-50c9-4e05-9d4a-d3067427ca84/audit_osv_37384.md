# [H] xfs: save ailp before dropping the AIL lock in push callbacks

## Summary
Severity: High
Advisory: CVE-2026-31454
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31454
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: save ailp before dropping the AIL lock in push callbacks

In xfs_inode_item_push() and xfs_qm_dquot_logitem_push(), the AIL lock
is dropped to perform buffer IO. Once the cluster buffer no longer
protects the log item from reclaim, the log item may be freed by
background reclaim or the dquot shrinker. The subsequent spin_lock()
call dereferences lip->li_ailp, which is a use-after-free.

Fix this by saving the ailp pointer in a local variable while the AIL
lock is held and the log item is guaranteed to be valid.

## References
- https://git.kernel.org/stable/c/19437e4f7bb909afde832b39372aa2f3ce3cfd88
- https://git.kernel.org/stable/c/394d70b86fae9fe865e7e6d9540b7696f73aa9b6
- https://git.kernel.org/stable/c/4c7d50147316cf049462f327c4a3e9dc2b7f1dd0
- https://git.kernel.org/stable/c/50f5f056807b7bed74f4f307f2ca0ed92f3e556d
- https://git.kernel.org/stable/c/6dbe17f19c290a72ce57d5abc70e1fad0c3e14e5
- https://git.kernel.org/stable/c/75669e987137f49c99ca44406bf0200d1892dd16
- https://git.kernel.org/stable/c/d8fc60bbaf5aea1604bf9f4ed565da6a1ac7a87d
- https://git.kernel.org/stable/c/edd1637d4e3911ab6c760f553f2040fe72f61a13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
