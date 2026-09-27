# [H] btrfs: harden block_group::bg_list against list_del() races

## Summary
Severity: High
Advisory: CVE-2025-37856
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37856
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: harden block_group::bg_list against list_del() races

As far as I can tell, these calls of list_del_init() on bg_list cannot
run concurrently with btrfs_mark_bg_unused() or btrfs_mark_bg_to_reclaim(),
as they are in transaction error paths and situations where the block
group is readonly.

However, if there is any chance at all of racing with mark_bg_unused(),
or a different future user of bg_list, better to be safe than sorry.

Otherwise we risk the following interleaving (bg_list refcount in parens)

T1 (some random op)                       T2 (btrfs_mark_bg_unused)
                                        !list_empty(&bg->bg_list); (1)
list_del_init(&bg->bg_list); (1)
                                        list_move_tail (1)
btrfs_put_block_group (0)
                                        btrfs_delete_unused_bgs
                                             bg = list_first_entry
                                             list_del_init(&bg->bg_list);
                                             btrfs_put_block_group(bg); (-1)

Ultimately, this results in a broken ref count that hits zero one deref
early and the real final deref underflows the refcount, resulting in a WARNING.

## References
- https://git.kernel.org/stable/c/185fd73e5ac06027c4be9a129e59193f6a3ef202
- https://git.kernel.org/stable/c/7511e29cf1355b2c47d0effb39e463119913e2f6
- https://git.kernel.org/stable/c/909e60fb469d4101c6b08cf6e622efb062bb24a1
- https://git.kernel.org/stable/c/bf089c4d1141b27332c092b1dcca5022c415a3b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37856.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37856
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
