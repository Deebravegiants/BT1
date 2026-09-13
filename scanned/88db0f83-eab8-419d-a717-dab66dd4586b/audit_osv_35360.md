# [C] btrfs: fix use-after-free warning in btrfs_get_or_create_delayed_node()

## Summary
Severity: Critical
Advisory: CVE-2025-71159
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71159
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix use-after-free warning in btrfs_get_or_create_delayed_node()

Previously, btrfs_get_or_create_delayed_node() set the delayed_node's
refcount before acquiring the root->delayed_nodes lock.
Commit e8513c012de7 ("btrfs: implement ref_tracker for delayed_nodes")
moved refcount_set inside the critical section, which means there is
no longer a memory barrier between setting the refcount and setting
btrfs_inode->delayed_node.

Without that barrier, the stores to node->refs and
btrfs_inode->delayed_node may become visible out of order. Another
thread can then read btrfs_inode->delayed_node and attempt to
increment a refcount that hasn't been set yet, leading to a
refcounting bug and a use-after-free warning.

The fix is to move refcount_set back to where it was to take
advantage of the implicit memory barrier provided by lock
acquisition.

Because the allocations now happen outside of the lock's critical
section, they can use GFP_NOFS instead of GFP_ATOMIC.

## References
- https://git.kernel.org/stable/c/83f59076a1ae6f5c6845d6f7ed3a1a373d883684
- https://git.kernel.org/stable/c/c8385851a5435f4006281828d428e5d0b0bbf8af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71159.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
