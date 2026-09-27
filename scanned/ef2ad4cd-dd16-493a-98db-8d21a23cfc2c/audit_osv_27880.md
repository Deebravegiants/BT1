# [M] nilfs2: fix potential bug in end_buffer_async_write

## Summary
Severity: Medium
Advisory: CVE-2024-26685
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26685
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix potential bug in end_buffer_async_write

According to a syzbot report, end_buffer_async_write(), which handles the
completion of block device writes, may detect abnormal condition of the
buffer async_write flag and cause a BUG_ON failure when using nilfs2.

Nilfs2 itself does not use end_buffer_async_write().  But, the async_write
flag is now used as a marker by commit 7f42ec394156 ("nilfs2: fix issue
with race condition of competition between segments for dirty blocks") as
a means of resolving double list insertion of dirty blocks in
nilfs_lookup_dirty_data_buffers() and nilfs_lookup_node_buffers() and the
resulting crash.

This modification is safe as long as it is used for file data and b-tree
node blocks where the page caches are independent.  However, it was
irrelevant and redundant to also introduce async_write for segment summary
and super root blocks that share buffers with the backing device.  This
led to the possibility that the BUG_ON check in end_buffer_async_write
would fail as described above, if independent writebacks of the backing
device occurred in parallel.

The use of async_write for segment summary buffers has already been
removed in a previous change.

Fix this issue by removing the manipulation of the async_write flag for
the remaining super root block buffer.

## References
- https://git.kernel.org/stable/c/2c3bdba00283a6c7a5b19481a59a730f46063803
- https://git.kernel.org/stable/c/5bc09b397cbf1221f8a8aacb1152650c9195b02b
- https://git.kernel.org/stable/c/626daab3811b772086aef1bf8eed3ffe6f523eff
- https://git.kernel.org/stable/c/6589f0f72f8edd1fa11adce4eedbd3615f2e78ab
- https://git.kernel.org/stable/c/8fa90634ec3e9cc50f42dd605eec60f2d146ced8
- https://git.kernel.org/stable/c/c4a09fdac625e64abe478dcf88bfa20406616928
- https://git.kernel.org/stable/c/d31c8721e816eff5ca6573cc487754f357c093cd
- https://git.kernel.org/stable/c/f3e4963566f58726d3265a727116a42b591f6596
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26685.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26685
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
