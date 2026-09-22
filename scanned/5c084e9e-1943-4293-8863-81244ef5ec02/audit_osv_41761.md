# [H] f2fs: atomic: fix UAF issue on f2fs_inode_info.atomic_inode

## Summary
Severity: High
Advisory: CVE-2026-63816
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63816
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: atomic: fix UAF issue on f2fs_inode_info.atomic_inode

- ioctl(F2FS_IOC_GARBAGE_COLLECT_RANGE)		- shrink
 - f2fs_gc
  - gc_data_segment
   - ra_data_block(cow_inode)
    - mapping = F2FS_I(inode)->atomic_inode->i_mapping
    : f2fs_is_cow_file(cow_inode) is true
						 - f2fs_evict_inode(atomic_inode)
						  - clear_inode_flag(fi->cow_inode, FI_COW_FILE)
						  - F2FS_I(fi->cow_inode)->atomic_inode = NULL
						  ...
						  - truncate_inode_pages_final(atomic_inode)
    - f2fs_grab_cache_folio(mapping)
    : create folio in atomic_inode->mapping
						  - clear_inode(atomic_inode)
						   - BUG_ON(atomic_inode->i_data.nrpages)

We need to add a reference on fi->atomic_inode before using its mapping
field during garbage collection, otherwise, it will cause UAF issue.

## References
- https://git.kernel.org/stable/c/56038756aae68312df00d4aa1d97e51ef3aca725
- https://git.kernel.org/stable/c/7d3ae21783e5914c1761ac7d63f882d3d70800e9
- https://git.kernel.org/stable/c/a499f77c06050a28c897bdbd86cd2f0721ae0743
- https://git.kernel.org/stable/c/a805fec35c201c59643ddcde713bce4051c8ee27
- https://git.kernel.org/stable/c/e0288584baa5dc41df4a829a023c4c1b33fe53d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63816.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63816
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
