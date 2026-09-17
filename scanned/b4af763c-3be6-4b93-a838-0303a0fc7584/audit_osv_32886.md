# [H] f2fs: fix to do sanity check on sit_bitmap_size

## Summary
Severity: High
Advisory: CVE-2025-38218
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38218
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to do sanity check on sit_bitmap_size

w/ below testcase, resize will generate a corrupted image which
contains inconsistent metadata, so when mounting such image, it
will trigger kernel panic:

touch img
truncate -s $((512*1024*1024*1024)) img
mkfs.f2fs -f img $((256*1024*1024))
resize.f2fs -s -i img -t $((1024*1024*1024))
mount img /mnt/f2fs

------------[ cut here ]------------
kernel BUG at fs/f2fs/segment.h:863!
Oops: invalid opcode: 0000 [#1] SMP PTI
CPU: 11 UID: 0 PID: 3922 Comm: mount Not tainted 6.15.0-rc1+ #191 PREEMPT(voluntary)
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
RIP: 0010:f2fs_ra_meta_pages+0x47c/0x490

Call Trace:
 f2fs_build_segment_manager+0x11c3/0x2600
 f2fs_fill_super+0xe97/0x2840
 mount_bdev+0xf4/0x140
 legacy_get_tree+0x2b/0x50
 vfs_get_tree+0x29/0xd0
 path_mount+0x487/0xaf0
 __x64_sys_mount+0x116/0x150
 do_syscall_64+0x82/0x190
 entry_SYSCALL_64_after_hwframe+0x76/0x7e
RIP: 0033:0x7fdbfde1bcfe

The reaseon is:

sit_i->bitmap_size is 192, so size of sit bitmap is 192*8=1536, at maximum
there are 1536 sit blocks, however MAIN_SEGS is 261893, so that sit_blk_cnt
is 4762, build_sit_entries() -> current_sit_addr() tries to access
out-of-boundary in sit_bitmap at offset from [1536, 4762), once sit_bitmap
and sit_bitmap_mirror is not the same, it will trigger f2fs_bug_on().

Let's add sanity check in f2fs_sanity_check_ckpt() to avoid panic.

## References
- https://git.kernel.org/stable/c/38ef48a8afef8df646b6f6ae7abb872f18b533c1
- https://git.kernel.org/stable/c/3e5ac62a56a24f4d88ce8ffd7bc452428b235868
- https://git.kernel.org/stable/c/5db0d252c64e91ba1929c70112352e85dc5751e7
- https://git.kernel.org/stable/c/79ef8a6c4ec53d327580fd7d2b522cf4f1d05b0c
- https://git.kernel.org/stable/c/82f51bff393e4c12cf4de553120ca831cfa4ef19
- https://git.kernel.org/stable/c/ad862f71016ba38039df1c96ed55c0a4314cc183
- https://git.kernel.org/stable/c/ee1b421c469876544e297ec1090574bd76100247
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38218.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38218
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
