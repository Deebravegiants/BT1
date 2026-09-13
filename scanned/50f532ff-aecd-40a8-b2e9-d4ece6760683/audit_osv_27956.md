# [H] f2fs: fix to truncate meta inode pages forcely

## Summary
Severity: High
Advisory: CVE-2024-26869
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26869
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to truncate meta inode pages forcely

Below race case can cause data corruption:

Thread A				GC thread
					- gc_data_segment
					 - ra_data_block
					  - locked meta_inode page
- f2fs_inplace_write_data
 - invalidate_mapping_pages
 : fail to invalidate meta_inode page
   due to lock failure or dirty|writeback
   status
 - f2fs_submit_page_bio
 : write last dirty data to old blkaddr
					 - move_data_block
					  - load old data from meta_inode page
					  - f2fs_submit_page_write
					  : write old data to new blkaddr

Because invalidate_mapping_pages() will skip invalidating page which
has unclear status including locked, dirty, writeback and so on, so
we need to use truncate_inode_pages_range() instead of
invalidate_mapping_pages() to make sure meta_inode page will be dropped.

## References
- https://git.kernel.org/stable/c/04226d8e3c4028dc451e9d8777356ec0f7919253
- https://git.kernel.org/stable/c/77bfdb89cc222fc7bfe198eda77bdc427d5ac189
- https://git.kernel.org/stable/c/9f0c4a46be1fe9b97dbe66d49204c1371e3ece65
- https://git.kernel.org/stable/c/c92f2927df860a60ba815d3ee610a944b92a8694
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26869.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26869
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
