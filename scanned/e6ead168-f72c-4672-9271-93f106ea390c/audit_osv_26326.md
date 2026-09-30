# [H] f2fs: compress: fix to avoid use-after-free on dic

## Summary
Severity: High
Advisory: CVE-2023-52852
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52852
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: fix to avoid use-after-free on dic

Call trace:
 __memcpy+0x128/0x250
 f2fs_read_multi_pages+0x940/0xf7c
 f2fs_mpage_readpages+0x5a8/0x624
 f2fs_readahead+0x5c/0x110
 page_cache_ra_unbounded+0x1b8/0x590
 do_sync_mmap_readahead+0x1dc/0x2e4
 filemap_fault+0x254/0xa8c
 f2fs_filemap_fault+0x2c/0x104
 __do_fault+0x7c/0x238
 do_handle_mm_fault+0x11bc/0x2d14
 do_mem_abort+0x3a8/0x1004
 el0_da+0x3c/0xa0
 el0t_64_sync_handler+0xc4/0xec
 el0t_64_sync+0x1b4/0x1b8

In f2fs_read_multi_pages(), once f2fs_decompress_cluster() was called if
we hit cached page in compress_inode's cache, dic may be released, it needs
break the loop rather than continuing it, in order to avoid accessing
invalid dic pointer.

## References
- https://git.kernel.org/stable/c/8c4504cc0c64862740a6acb301e0cfa59580dbc5
- https://git.kernel.org/stable/c/932ddb5c29e884cc6fac20417ece72ba4a35c401
- https://git.kernel.org/stable/c/9375ea7f269093d7c884857ae1f47633a91f429c
- https://git.kernel.org/stable/c/9d065aa52b6ee1b06f9c4eca881c9b4425a12ba2
- https://git.kernel.org/stable/c/b0327c84e91a0f4f0abced8cb83ec86a7083f086
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52852.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52852
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
