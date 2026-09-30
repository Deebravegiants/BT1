# [H] ocfs2: fix races between hole punching and AIO+DIO

## Summary
Severity: High
Advisory: CVE-2024-40943
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40943
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix races between hole punching and AIO+DIO

After commit "ocfs2: return real error code in ocfs2_dio_wr_get_block",
fstests/generic/300 become from always failed to sometimes failed:

========================================================================
[  473.293420 ] run fstests generic/300

[  475.296983 ] JBD2: Ignoring recovery information on journal
[  475.302473 ] ocfs2: Mounting device (253,1) on (node local, slot 0) with ordered data mode.
[  494.290998 ] OCFS2: ERROR (device dm-1): ocfs2_change_extent_flag: Owner 5668 has an extent at cpos 78723 which can no longer be found
[  494.291609 ] On-disk corruption discovered. Please run fsck.ocfs2 once the filesystem is unmounted.
[  494.292018 ] OCFS2: File system is now read-only.
[  494.292224 ] (kworker/19:11,2628,19):ocfs2_mark_extent_written:5272 ERROR: status = -30
[  494.292602 ] (kworker/19:11,2628,19):ocfs2_dio_end_io_write:2374 ERROR: status = -3
fio: io_u error on file /mnt/scratch/racer: Read-only file system: write offset=460849152, buflen=131072
=========================================================================

In __blockdev_direct_IO, ocfs2_dio_wr_get_block is called to add unwritten
extents to a list.  extents are also inserted into extent tree in
ocfs2_write_begin_nolock.  Then another thread call fallocate to puch a
hole at one of the unwritten extent.  The extent at cpos was removed by
ocfs2_remove_extent().  At end io worker thread, ocfs2_search_extent_list
found there is no such extent at the cpos.

    T1                        T2                T3
                              inode lock
                                ...
                                insert extents
                                ...
                              inode unlock
ocfs2_fallocate
 __ocfs2_change_file_space
  inode lock
  lock ip_alloc_sem
  ocfs2_remove_inode_range inode
   ocfs2_remove_btree_range
    ocfs2_remove_extent
    ^---remove the extent at cpos 78723
  ...
  unlock ip_alloc_sem
  inode unlock
                                       ocfs2_dio_end_io
                                        ocfs2_dio_end_io_write
                                         lock ip_alloc_sem
                                         ocfs2_mark_extent_written
                                          ocfs2_change_extent_flag
                                           ocfs2_search_extent_list
                                           ^---failed to find extent
                                          ...
                                          unlock ip_alloc_sem

In most filesystems, fallocate is not compatible with racing with AIO+DIO,
so fix it by adding to wait for all dio before fallocate/punch_hole like
ext4.

## References
- https://git.kernel.org/stable/c/050ce8af6838c71e872e982b50d3f1bec21da40e
- https://git.kernel.org/stable/c/117b9c009b72a6c2ebfd23484354dfee2d9570d2
- https://git.kernel.org/stable/c/38825ff9da91d2854dcf6d9ac320a7e641e10f25
- https://git.kernel.org/stable/c/3c26b5d21b1239e9c7fd31ba7d9b2d7bdbaa68d9
- https://git.kernel.org/stable/c/3c361f313d696df72f9bccf058510e9ec737b9b1
- https://git.kernel.org/stable/c/952b023f06a24b2ad6ba67304c4c84d45bea2f18
- https://git.kernel.org/stable/c/e8e2db1adac47970a6a9225f3858e9aa0e86287f
- https://git.kernel.org/stable/c/ea042dc2bea19d72e37c298bf65a9c341ef3fff3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40943.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40943
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
