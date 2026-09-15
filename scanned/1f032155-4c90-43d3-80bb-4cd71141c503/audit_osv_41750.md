# [H] blk-cgroup: fix UAF in __blkcg_rstat_flush()

## Summary
Severity: High
Advisory: CVE-2026-63802
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63802
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: fix UAF in __blkcg_rstat_flush()

When multiple blkgs in the same blkcg are released concurrently,
a use-after-free can occur. The race happens when one blkg's
__blkcg_rstat_flush() removes another blkg's iostat entries via
llist_del_all(). The second blkg sees an empty list and proceeds
to free itself while the first is still iterating over its entries.

Move the flush from __blkg_release() (RCU callback) to blkg_release()
(before call_rcu). This ensures the RCU grace period waits for any
concurrent flush's rcu_read_lock() section to complete before freeing.

## References
- https://git.kernel.org/stable/c/0ab5ee5a1badb58cbb2242617cb01a4972b1f2a2
- https://git.kernel.org/stable/c/5e5b7f2ef854936e95dceb6a2fdfefcb7152d2c6
- https://git.kernel.org/stable/c/96e545410c4f74c89d496c1d5d9ef8d08f14368b
- https://git.kernel.org/stable/c/afebe44facc48a61761e885bbb7f0380d4a603ec
- https://git.kernel.org/stable/c/bbebd9425cad3573d1527441753899b926525a0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63802.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63802
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
