# [H] netfs: Fix early read unlock of page with EOF in middle

## Summary
Severity: High
Advisory: CVE-2025-71201
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2025-71201
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix early read unlock of page with EOF in middle

The read result collection for buffered reads seems to run ahead of the
completion of subrequests under some circumstances, as can be seen in the
following log snippet:

    9p_client_res: client 18446612686390831168 response P9_TREAD tag  0 err 0
    ...
    netfs_sreq: R=00001b55[1] DOWN TERM  f=192 s=0 5fb2/5fb2 s=5 e=0
    ...
    netfs_collect_folio: R=00001b55 ix=00004 r=4000-5000 t=4000/5fb2
    netfs_folio: i=157f3 ix=00004-00004 read-done
    netfs_folio: i=157f3 ix=00004-00004 read-unlock
    netfs_collect_folio: R=00001b55 ix=00005 r=5000-5fb2 t=5000/5fb2
    netfs_folio: i=157f3 ix=00005-00005 read-done
    netfs_folio: i=157f3 ix=00005-00005 read-unlock
    ...
    netfs_collect_stream: R=00001b55[0:] cto=5fb2 frn=ffffffff
    netfs_collect_state: R=00001b55 col=5fb2 cln=6000 n=c
    netfs_collect_stream: R=00001b55[0:] cto=5fb2 frn=ffffffff
    netfs_collect_state: R=00001b55 col=5fb2 cln=6000 n=8
    ...
    netfs_sreq: R=00001b55[2] ZERO SUBMT f=000 s=5fb2 0/4e s=0 e=0
    netfs_sreq: R=00001b55[2] ZERO TERM  f=102 s=5fb2 4e/4e s=5 e=0

The 'cto=5fb2' indicates the collected file pos we've collected results to
so far - but we still have 0x4e more bytes to go - so we shouldn't have
collected folio ix=00005 yet.  The 'ZERO' subreq that clears the tail
happens after we unlock the folio, allowing the application to see the
uncleared tail through mmap.

The problem is that netfs_read_unlock_folios() will unlock a folio in which
the amount of read results collected hits EOF position - but the ZERO
subreq lies beyond that and so happens after.

Fix this by changing the end check to always be the end of the folio and
never the end of the file.

In the future, I should look at clearing to the end of the folio here rather
than adding a ZERO subreq to do this.  On the other hand, the ZERO subreq can
run in parallel with an async READ subreq.  Further, the ZERO subreq may still
be necessary to, say, handle extents in a ceph file that don't have any
backing store and are thus implicitly all zeros.

This can be reproduced by creating a file, the size of which doesn't align
to a page boundary, e.g. 24998 (0x5fb2) bytes and then doing something
like:

    xfs_io -c "mmap -r 0 0x6000" -c "madvise -d 0 0x6000" \
           -c "mread -v 0 0x6000" /xfstest.test/x

The last 0x4e bytes should all be 00, but if the tail hasn't been cleared
yet, you may see rubbish there.  This can be reproduced with kafs by
modifying the kernel to disable the call to netfs_read_subreq_progress()
and to stop afs_issue_read() from doing the async call for NETFS_READAHEAD.
Reproduction can be made easier by inserting an mdelay(100) in
netfs_issue_read() for the ZERO-subreq case.

AFS and CIFS are normally unlikely to show this as they dispatch READ ops
asynchronously, which allows the ZERO-subreq to finish first.  9P's READ op is
completely synchronous, so the ZERO-subreq will always happen after.  It isn't
seen all the time, though, because the collection may be done in a worker
thread.

## References
- https://git.kernel.org/stable/c/570ad253a3455a520f03c2136af8714bc780186d
- https://git.kernel.org/stable/c/5b5482c0e5ee740b35a70759d3582477aea8e8e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71201.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
