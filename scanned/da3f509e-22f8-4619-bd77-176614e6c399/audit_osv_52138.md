# [M] CVE-2021-47114

## Summary
Severity: Medium
Advisory: CVE-2021-47114
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47114
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix data corruption by fallocate

When fallocate punches holes out of inode size, if original isize is in
the middle of last cluster, then the part from isize to the end of the
cluster will be zeroed with buffer write, at that time isize is not yet
updated to match the new size, if writeback is kicked in, it will invoke
ocfs2_writepage()->block_write_full_page() where the pages out of inode
size will be dropped.  That will cause file corruption.  Fix this by
zero out eof blocks when extending the inode size.

Running the following command with qemu-image 4.2.1 can get a corrupted
coverted image file easily.

    qemu-img convert -p -t none -T none -f qcow2 $qcow_image \
             -O qcow2 -o compat=1.1 $qcow_image.conv

The usage of fallocate in qemu is like this, it first punches holes out
of inode size, then extend the inode size.

    fallocate(11, FALLOC_FL_KEEP_SIZE|FALLOC_FL_PUNCH_HOLE, 2276196352, 65536) = 0
    fallocate(11, 0, 2276196352, 65536) = 0

v1: https://www.spinics.net/lists/linux-fsdevel/msg193999.html
v2: https://lore.kernel.org/linux-fsdevel/20210525093034.GB4112@quack2.suse.cz/T/

## References
- https://git.kernel.org/stable/c/c8d5faee46242c3f33b8a71a4d7d52214785bfcc
- https://git.kernel.org/stable/c/cc2edb99ea606a45182b5ea38cc8f4e583aa0774
- https://git.kernel.org/stable/c/cec4e857ffaa8c447f51cd8ab4e72350077b6770
- https://git.kernel.org/stable/c/0a31dd6fd2f4e7db538fb6eb1f06973d81f8dd3b
- https://git.kernel.org/stable/c/33e03adafb29eedae1bae9cdb50c1385279fcf65
- https://git.kernel.org/stable/c/624fa7baa3788dc9e57840ba5b94bc22b03cda57
- https://git.kernel.org/stable/c/6bba4471f0cc1296fe3c2089b9e52442d3074b2e
- https://git.kernel.org/stable/c/a1700479524bb9cb5e8ae720236a6fabd003acae
