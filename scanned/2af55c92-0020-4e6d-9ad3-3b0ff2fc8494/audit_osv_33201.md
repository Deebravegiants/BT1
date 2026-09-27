# [M] btrfs: fix subvolume deletion lockup caused by inodes xarray race

## Summary
Severity: Medium
Advisory: CVE-2025-39884
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39884
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix subvolume deletion lockup caused by inodes xarray race

There is a race condition between inode eviction and inode caching that
can cause a live struct btrfs_inode to be missing from the root->inodes
xarray. Specifically, there is a window during evict() between the inode
being unhashed and deleted from the xarray. If btrfs_iget() is called
for the same inode in that window, it will be recreated and inserted
into the xarray, but then eviction will delete the new entry, leaving
nothing in the xarray:

Thread 1                          Thread 2
---------------------------------------------------------------
evict()
  remove_inode_hash()
                                  btrfs_iget_path()
                                    btrfs_iget_locked()
                                    btrfs_read_locked_inode()
                                      btrfs_add_inode_to_root()
  destroy_inode()
    btrfs_destroy_inode()
      btrfs_del_inode_from_root()
        __xa_erase

In turn, this can cause issues for subvolume deletion. Specifically, if
an inode is in this lost state, and all other inodes are evicted, then
btrfs_del_inode_from_root() will call btrfs_add_dead_root() prematurely.
If the lost inode has a delayed_node attached to it, then when
btrfs_clean_one_deleted_snapshot() calls btrfs_kill_all_delayed_nodes(),
it will loop forever because the delayed_nodes xarray will never become
empty (unless memory pressure forces the inode out). We saw this
manifest as soft lockups in production.

Fix it by only deleting the xarray entry if it matches the given inode
(using __xa_cmpxchg()).

## References
- https://git.kernel.org/stable/c/9ba898c9fcbe6ebb88bcd4df8aab0f90090d202e
- https://git.kernel.org/stable/c/f1498abaf74f8d7b1e7001f16ed77818d8ae6a59
- https://git.kernel.org/stable/c/f6a6c280059c4ddc23e12e3de1b01098e240036f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39884.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39884
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
