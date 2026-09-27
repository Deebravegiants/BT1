# [M] NFS: fix nfs_release_folio() to not deadlock via kcompactd writeback

## Summary
Severity: Medium
Advisory: CVE-2025-21908
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21908
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: fix nfs_release_folio() to not deadlock via kcompactd writeback

Add PF_KCOMPACTD flag and current_is_kcompactd() helper to check for it so
nfs_release_folio() can skip calling nfs_wb_folio() from kcompactd.

Otherwise NFS can deadlock waiting for kcompactd enduced writeback which
recurses back to NFS (which triggers writeback to NFSD via NFS loopback
mount on the same host, NFSD blocks waiting for XFS's call to
__filemap_get_folio):

6070.550357] INFO: task kcompactd0:58 blocked for more than 4435 seconds.

{---
[58] "kcompactd0"
[<0>] folio_wait_bit+0xe8/0x200
[<0>] folio_wait_writeback+0x2b/0x80
[<0>] nfs_wb_folio+0x80/0x1b0 [nfs]
[<0>] nfs_release_folio+0x68/0x130 [nfs]
[<0>] split_huge_page_to_list_to_order+0x362/0x840
[<0>] migrate_pages_batch+0x43d/0xb90
[<0>] migrate_pages_sync+0x9a/0x240
[<0>] migrate_pages+0x93c/0x9f0
[<0>] compact_zone+0x8e2/0x1030
[<0>] compact_node+0xdb/0x120
[<0>] kcompactd+0x121/0x2e0
[<0>] kthread+0xcf/0x100
[<0>] ret_from_fork+0x31/0x40
[<0>] ret_from_fork_asm+0x1a/0x30
---}

[akpm@linux-foundation.org: fix build]

## References
- https://git.kernel.org/stable/c/5ae31c54cff745832b9bd5b32e71f3d1b607cd1e
- https://git.kernel.org/stable/c/8253ff29edcb429a9a6c75710941c6a16a9a34b1
- https://git.kernel.org/stable/c/ab0727d6e2196682351c25c1dd112136f6991f11
- https://git.kernel.org/stable/c/ce6d9c1c2b5cc785016faa11b48b6cd317eb367e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21908.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
