# [H] f2fs: fix to bail out in get_new_segment()

## Summary
Severity: High
Advisory: CVE-2025-38333
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38333
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to bail out in get_new_segment()

------------[ cut here ]------------
WARNING: CPU: 3 PID: 579 at fs/f2fs/segment.c:2832 new_curseg+0x5e8/0x6dc
pc : new_curseg+0x5e8/0x6dc
Call trace:
 new_curseg+0x5e8/0x6dc
 f2fs_allocate_data_block+0xa54/0xe28
 do_write_page+0x6c/0x194
 f2fs_do_write_node_page+0x38/0x78
 __write_node_page+0x248/0x6d4
 f2fs_sync_node_pages+0x524/0x72c
 f2fs_write_checkpoint+0x4bc/0x9b0
 __checkpoint_and_complete_reqs+0x80/0x244
 issue_checkpoint_thread+0x8c/0xec
 kthread+0x114/0x1bc
 ret_from_fork+0x10/0x20

get_new_segment() detects inconsistent status in between free_segmap
and free_secmap, let's record such error into super block, and bail
out get_new_segment() instead of continue using the segment.

## References
- https://git.kernel.org/stable/c/bb5eb8a5b222fa5092f60d5555867a05ebc3bdf2
- https://git.kernel.org/stable/c/ca860f507a61c7c3d4dde47b830a5c0d555cf83c
- https://git.kernel.org/stable/c/f0023d7a2a86999c8e1300e911d92f995a5310a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38333.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38333
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
