# [H] btrfs: reject free space cache with more entries than pages

## Summary
Severity: High
Advisory: CVE-2026-64567
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64567
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: reject free space cache with more entries than pages

When loading a v1 free space cache, __load_free_space_cache() takes
num_entries and num_bitmaps straight from the on-disk
btrfs_free_space_header. That header is stored in the tree_root under a key
with type 0, which the tree-checker has no case for, so neither count is
validated before the load trusts it.

The load loops num_entries times and maps the next page whenever the current
one runs out, going through io_ctl_check_crc() -> io_ctl_map_page(), which
does io_ctl->pages[io_ctl->index++]. But pages[] is allocated in
io_ctl_init() from the cache inode's i_size, not from num_entries:

	num_pages = DIV_ROUND_UP(i_size_read(inode), PAGE_SIZE);
	io_ctl->pages = kcalloc(num_pages, sizeof(struct page *), GFP_NOFS);

So if num_entries claims more records than the pages can hold, io_ctl->index
runs off the end of pages[]. The write side never hits this because
io_ctl_add_entry() and io_ctl_add_bitmap() both stop once
io_ctl->index >= io_ctl->num_pages; the read side just never had the same
check.

To trigger it, take a clean cache (num_entries = <N> here), set num_entries
in the header to 0x10000, and fix up the leaf checksum so it still passes
the tree-checker. The cache inode has i_size = 65536, so num_pages is 16 and
pages[] is a 16-pointer (kmalloc-128) array. The load now tries to read
65536 entries, io_ctl->index walks up to 16, and pages[16] is read past the
array:

  BUG: KASAN: slab-out-of-bounds in io_ctl_check_crc (fs/btrfs/free-space-cache.c:420 fs/btrfs/free-space-cache.c:565)
  Read of size 8 at addr ffff88800c833a80 by task kworker/u8:3/58
   io_ctl_check_crc (fs/btrfs/free-space-cache.c:420 fs/btrfs/free-space-cache.c:565)
   __load_free_space_cache (fs/btrfs/free-space-cache.c:655 fs/btrfs/free-space-cache.c:820)
   load_free_space_cache (fs/btrfs/free-space-cache.c:1017)
   caching_thread (fs/btrfs/block-group.c:880)
   btrfs_work_helper (fs/btrfs/async-thread.c:312)
   process_one_work
   worker_thread
   kthread
   ret_from_fork

free-space-cache.c:420 is io_ctl_map_page(), inlined into io_ctl_check_crc()
at line 565, which is why that is the frame KASAN names. The out-of-bounds
slot is then treated as a struct page and handed to crc32c(), so the bad
read turns into a GP fault.

Add the missing check to io_ctl_check_crc(), which is where both the entry
loop and the bitmap loop end up. When num_entries is too large the load now
fails like any corrupt cache: __load_free_space_cache() drops it and rebuilds
the free space from the extent tree, so a valid cache is never rejected.

## References
- https://git.kernel.org/stable/c/094734c7aaa2b36751dc32480a680a4952685e78
- https://git.kernel.org/stable/c/33878ba25e2638bc0c61623d7a05c9ca2b74c039
- https://git.kernel.org/stable/c/404a0b986e0b6e79738fdf1f0ebbbc43b9acd2a2
- https://git.kernel.org/stable/c/5e1b2ca6b34939e70fb0785e8222b53cf060016f
- https://git.kernel.org/stable/c/8ded74c654a982dc8581a17b0caa7fcedb20de69
- https://git.kernel.org/stable/c/a2d8d5647ed854e38f941741aea45b9eb15a6350
- https://git.kernel.org/stable/c/c9c38066b6446e83668c041702bb639b0ca49363
- https://git.kernel.org/stable/c/f9fef131fa3f59b857217f522fa5ea430d1b707c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64567.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64567
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
