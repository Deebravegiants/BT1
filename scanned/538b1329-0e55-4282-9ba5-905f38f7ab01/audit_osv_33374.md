# [H] ocfs2: clear extent cache after moving/defragmenting extents

## Summary
Severity: High
Advisory: CVE-2025-40233
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40233
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.115, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: clear extent cache after moving/defragmenting extents

The extent map cache can become stale when extents are moved or
defragmented, causing subsequent operations to see outdated extent flags. 
This triggers a BUG_ON in ocfs2_refcount_cal_cow_clusters().

The problem occurs when:
1. copy_file_range() creates a reflinked extent with OCFS2_EXT_REFCOUNTED
2. ioctl(FITRIM) triggers ocfs2_move_extents()
3. __ocfs2_move_extents_range() reads and caches the extent (flags=0x2)
4. ocfs2_move_extent()/ocfs2_defrag_extent() calls __ocfs2_move_extent()
   which clears OCFS2_EXT_REFCOUNTED flag on disk (flags=0x0)
5. The extent map cache is not invalidated after the move
6. Later write() operations read stale cached flags (0x2) but disk has
   updated flags (0x0), causing a mismatch
7. BUG_ON(!(rec->e_flags & OCFS2_EXT_REFCOUNTED)) triggers

Fix by clearing the extent map cache after each extent move/defrag
operation in __ocfs2_move_extents_range().  This ensures subsequent
operations read fresh extent data from disk.

## References
- https://git.kernel.org/stable/c/78a63493f8e352296dbc7cb7b3f4973105e8679e
- https://git.kernel.org/stable/c/93166bc53c0e3587058327a4121daea34b4fecd5
- https://git.kernel.org/stable/c/93b1ab422f1966b71561158e1aedce4ec100f357
- https://git.kernel.org/stable/c/a21750df2f6169af6e039a3bb4893d6c9564e48d
- https://git.kernel.org/stable/c/a7ee72286efba1d407c6f15a0528e43593fb7007
- https://git.kernel.org/stable/c/aa6a21409dd6221bb268b56bb410e031c632ff9a
- https://git.kernel.org/stable/c/bb69928ed578f881e68d26aaf1a8f6e7faab3b44
- https://git.kernel.org/stable/c/e92af7737a94a729225d2a5d180eaaa77fe0bbc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40233.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
