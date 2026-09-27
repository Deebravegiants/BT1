# [H] ext4: fix double brelse() the buffer of the extents path

## Summary
Severity: High
Advisory: CVE-2024-49882
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49882
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix double brelse() the buffer of the extents path

In ext4_ext_try_to_merge_up(), set path[1].p_bh to NULL after it has been
released, otherwise it may be released twice. An example of what triggers
this is as follows:

  split2    map    split1
|--------|-------|--------|

ext4_ext_map_blocks
 ext4_ext_handle_unwritten_extents
  ext4_split_convert_extents
   // path->p_depth == 0
   ext4_split_extent
     // 1. do split1
     ext4_split_extent_at
       |ext4_ext_insert_extent
       |  ext4_ext_create_new_leaf
       |    ext4_ext_grow_indepth
       |      le16_add_cpu(&neh->eh_depth, 1)
       |    ext4_find_extent
       |      // return -ENOMEM
       |// get error and try zeroout
       |path = ext4_find_extent
       |  path->p_depth = 1
       |ext4_ext_try_to_merge
       |  ext4_ext_try_to_merge_up
       |    path->p_depth = 0
       |    brelse(path[1].p_bh)  ---> not set to NULL here
       |// zeroout success
     // 2. update path
     ext4_find_extent
     // 3. do split2
     ext4_split_extent_at
       ext4_ext_insert_extent
         ext4_ext_create_new_leaf
           ext4_ext_grow_indepth
             le16_add_cpu(&neh->eh_depth, 1)
           ext4_find_extent
             path[0].p_bh = NULL;
             path->p_depth = 1
             read_extent_tree_block  ---> return err
             // path[1].p_bh is still the old value
             ext4_free_ext_path
               ext4_ext_drop_refs
                 // path->p_depth == 1
                 brelse(path[1].p_bh)  ---> brelse a buffer twice

Finally got the following WARRNING when removing the buffer from lru:

============================================
VFS: brelse: Trying to free free buffer
WARNING: CPU: 2 PID: 72 at fs/buffer.c:1241 __brelse+0x58/0x90
CPU: 2 PID: 72 Comm: kworker/u19:1 Not tainted 6.9.0-dirty #716
RIP: 0010:__brelse+0x58/0x90
Call Trace:
 <TASK>
 __find_get_block+0x6e7/0x810
 bdev_getblk+0x2b/0x480
 __ext4_get_inode_loc+0x48a/0x1240
 ext4_get_inode_loc+0xb2/0x150
 ext4_reserve_inode_write+0xb7/0x230
 __ext4_mark_inode_dirty+0x144/0x6a0
 ext4_ext_insert_extent+0x9c8/0x3230
 ext4_ext_map_blocks+0xf45/0x2dc0
 ext4_map_blocks+0x724/0x1700
 ext4_do_writepages+0x12d6/0x2a70
[...]
============================================

## References
- https://git.kernel.org/stable/c/230ee0535d01478bad9a3037292043f39b9be10b
- https://git.kernel.org/stable/c/32bbb59e3f18facd7201bef110010bf35819b8c3
- https://git.kernel.org/stable/c/68a69cf60660c73990c1875f94a5551600b04775
- https://git.kernel.org/stable/c/7633407ca4ab8be2916ab214eb44ccebc6a50e1a
- https://git.kernel.org/stable/c/78bbc3d15b6f443acb26e94418c445bac940d414
- https://git.kernel.org/stable/c/b6c29c8f3d7cb67b505f3b2f6c242d52298d1f2e
- https://git.kernel.org/stable/c/d4574bda63906bf69660e001470bfe1a0ac524ae
- https://git.kernel.org/stable/c/dcaa6c31134c0f515600111c38ed7750003e1b9c
- https://git.kernel.org/stable/c/f9fd47c9d9548f9e47fa60098eab99dde175401d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49882.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49882
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
