# [H] ext4: fix slab-use-after-free in ext4_split_extent_at()

## Summary
Severity: High
Advisory: CVE-2024-49884
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49884
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.323, >=4.20.0 <5.4.290, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix slab-use-after-free in ext4_split_extent_at()

We hit the following use-after-free:

==================================================================
BUG: KASAN: slab-use-after-free in ext4_split_extent_at+0xba8/0xcc0
Read of size 2 at addr ffff88810548ed08 by task kworker/u20:0/40
CPU: 0 PID: 40 Comm: kworker/u20:0 Not tainted 6.9.0-dirty #724
Call Trace:
 <TASK>
 kasan_report+0x93/0xc0
 ext4_split_extent_at+0xba8/0xcc0
 ext4_split_extent.isra.0+0x18f/0x500
 ext4_split_convert_extents+0x275/0x750
 ext4_ext_handle_unwritten_extents+0x73e/0x1580
 ext4_ext_map_blocks+0xe20/0x2dc0
 ext4_map_blocks+0x724/0x1700
 ext4_do_writepages+0x12d6/0x2a70
[...]

Allocated by task 40:
 __kmalloc_noprof+0x1ac/0x480
 ext4_find_extent+0xf3b/0x1e70
 ext4_ext_map_blocks+0x188/0x2dc0
 ext4_map_blocks+0x724/0x1700
 ext4_do_writepages+0x12d6/0x2a70
[...]

Freed by task 40:
 kfree+0xf1/0x2b0
 ext4_find_extent+0xa71/0x1e70
 ext4_ext_insert_extent+0xa22/0x3260
 ext4_split_extent_at+0x3ef/0xcc0
 ext4_split_extent.isra.0+0x18f/0x500
 ext4_split_convert_extents+0x275/0x750
 ext4_ext_handle_unwritten_extents+0x73e/0x1580
 ext4_ext_map_blocks+0xe20/0x2dc0
 ext4_map_blocks+0x724/0x1700
 ext4_do_writepages+0x12d6/0x2a70
[...]
==================================================================

The flow of issue triggering is as follows:

ext4_split_extent_at
  path = *ppath
  ext4_ext_insert_extent(ppath)
    ext4_ext_create_new_leaf(ppath)
      ext4_find_extent(orig_path)
        path = *orig_path
        read_extent_tree_block
          // return -ENOMEM or -EIO
        ext4_free_ext_path(path)
          kfree(path)
        *orig_path = NULL
  a. If err is -ENOMEM:
  ext4_ext_dirty(path + path->p_depth)
  // path use-after-free !!!
  b. If err is -EIO and we have EXT_DEBUG defined:
  ext4_ext_show_leaf(path)
    eh = path[depth].p_hdr
    // path also use-after-free !!!

So when trying to zeroout or fix the extent length, call ext4_find_extent()
to update the path.

In addition we use *ppath directly as an ext4_ext_show_leaf() input to
avoid possible use-after-free when EXT_DEBUG is defined, and to avoid
unnecessary path updates.

## References
- https://git.kernel.org/stable/c/393a46f60ea4f249dc9d496d4eb2d542f5e11ade
- https://git.kernel.org/stable/c/448100a29395b0c8b4c42967155849fe0fbe808f
- https://git.kernel.org/stable/c/5d949ea75bb529ea6342e83465938a3b0ac51238
- https://git.kernel.org/stable/c/8fe117790b37c84c651e2bad9efc0e7fda73c0e3
- https://git.kernel.org/stable/c/915ac3630488af0ca194dc63b86d99802b4f6e18
- https://git.kernel.org/stable/c/a5401d4c3e2a3d25643c567d26e6de327774a2c9
- https://git.kernel.org/stable/c/c26ab35702f8cd0cdc78f96aa5856bfb77be798f
- https://git.kernel.org/stable/c/cafcc1bd62934547c76abf46c6d0d54f135006fe
- https://git.kernel.org/stable/c/e52f933598b781d291b9297e39c463536da0e185
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49884.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49884
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
