# [H] btrfs: ensure no dirty metadata is written back for an fs with errors

## Summary
Severity: High
Advisory: CVE-2025-40303
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40303
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: ensure no dirty metadata is written back for an fs with errors

[BUG]
During development of a minor feature (make sure all btrfs_bio::end_io()
is called in task context), I noticed a crash in generic/388, where
metadata writes triggered new works after btrfs_stop_all_workers().

It turns out that it can even happen without any code modification, just
using RAID5 for metadata and the same workload from generic/388 is going
to trigger the use-after-free.

[CAUSE]
If btrfs hits an error, the fs is marked as error, no new
transaction is allowed thus metadata is in a frozen state.

But there are some metadata modifications before that error, and they are
still in the btree inode page cache.

Since there will be no real transaction commit, all those dirty folios
are just kept as is in the page cache, and they can not be invalidated
by invalidate_inode_pages2() call inside close_ctree(), because they are
dirty.

And finally after btrfs_stop_all_workers(), we call iput() on btree
inode, which triggers writeback of those dirty metadata.

And if the fs is using RAID56 metadata, this will trigger RMW and queue
new works into rmw_workers, which is already stopped, causing warning
from queue_work() and use-after-free.

[FIX]
Add a special handling for write_one_eb(), that if the fs is already in
an error state, immediately mark the bbio as failure, instead of really
submitting them.

Then during close_ctree(), iput() will just discard all those dirty
tree blocks without really writing them back, thus no more new jobs for
already stopped-and-freed workqueues.

The extra discard in write_one_eb() also acts as an extra safenet.
E.g. the transaction abort is triggered by some extent/free space
tree corruptions, and since extent/free space tree is already corrupted
some tree blocks may be allocated where they shouldn't be (overwriting
existing tree blocks). In that case writing them back will further
corrupting the fs.

## References
- https://git.kernel.org/stable/c/066ee13f05fbd82ada01883e51f0695172f98dff
- https://git.kernel.org/stable/c/2618849f31e7cf51fadd4a5242458501a6d5b315
- https://git.kernel.org/stable/c/54a5b5a15588e3b0b294df31474d08a2678d4291
- https://git.kernel.org/stable/c/e2b3859067bf012d53c49b3f885fef40624a2c83
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40303.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
