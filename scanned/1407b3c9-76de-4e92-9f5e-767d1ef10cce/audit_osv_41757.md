# [H] f2fs: fix incorrect FI_NO_EXTENT handling in __destroy_extent_node()

## Summary
Severity: High
Advisory: CVE-2026-63812
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63812
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix incorrect FI_NO_EXTENT handling in __destroy_extent_node()

When __destroy_extent_node() sets the inode flag FI_NO_EXTENT, it does
not reset the length of the largest extent to 0 and update the inode
folio. Since modifications to the extent tree are disallowed afterward,
the cached largest extent may become stale. This can trigger the
following error in xfstests generic/388:

F2FS-fs (dm-0): sanity_check_extent_cache: inode (ino=1761) extent info [220057, 57, 6] is incorrect, run fsck to fix

In the f2fs_drop_inode path, __destroy_extent_node() does not need to
guarantee that et->node_cnt is 0, because concurrency with writeback
is expected in this path, and writeback may update the extent cache.

This patch reverts commit ed78aeebef05 ("f2fs: fix node_cnt race between
extent node destroy and writeback"), and remove the unnecessary zero
check of et->node_cnt.

## References
- https://git.kernel.org/stable/c/1f70ddb28a3c71df124da5fa4040c808116d6bb9
- https://git.kernel.org/stable/c/20190e498057997532c7f186d081011f18e0a462
- https://git.kernel.org/stable/c/58a5deb220bcac4c73bf58954c0845644c997487
- https://git.kernel.org/stable/c/7e4d8f98be63f98856a5176b9188dada6e7ba9ee
- https://git.kernel.org/stable/c/edf12cbeeeabe799bd2ee21fdb5c336cce6fbad7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63812.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63812
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
