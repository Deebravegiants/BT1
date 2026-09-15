# [H] netfs: Fix the pre-flush when appending to a file in writethrough mode

## Summary
Severity: High
Advisory: CVE-2024-36001
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-36001
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix the pre-flush when appending to a file in writethrough mode

In netfs_perform_write(), when the file is marked NETFS_ICTX_WRITETHROUGH
or O_*SYNC or RWF_*SYNC was specified, write-through caching is performed
on a buffered file.  When setting up for write-through, we flush any
conflicting writes in the region and wait for the write to complete,
failing if there's a write error to return.

The issue arises if we're writing at or above the EOF position because we
skip the flush and - more importantly - the wait.  This becomes a problem
if there's a partial folio at the end of the file that is being written out
and we want to make a write to it too.  Both the already-running write and
the write we start both want to clear the writeback mark, but whoever is
second causes a warning looking something like:

    ------------[ cut here ]------------
    R=00000012: folio 11 is not under writeback
    WARNING: CPU: 34 PID: 654 at fs/netfs/write_collect.c:105
    ...
    CPU: 34 PID: 654 Comm: kworker/u386:27 Tainted: G S ...
    ...
    Workqueue: events_unbound netfs_write_collection_worker
    ...
    RIP: 0010:netfs_writeback_lookup_folio

Fix this by making the flush-and-wait unconditional.  It will do nothing if
there are no folios in the pagecache and will return quickly if there are
no folios in the region specified.

Further, move the WBC attachment above the flush call as the flush is going
to attach a WBC and detach it again if it is not present - and since we
need one anyway we might as well share it.

## References
- https://git.kernel.org/stable/c/5eaf23b2e81349f6614f88396dc468fda89fc0b9
- https://git.kernel.org/stable/c/c97f59e276d4e93480f29a70accbd0d7273cf3f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36001.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36001
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
