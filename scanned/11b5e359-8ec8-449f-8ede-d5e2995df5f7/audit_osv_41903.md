# [C] netfs: Fix cancellation of a DIO and single read subrequests

## Summary
Severity: Critical
Advisory: CVE-2026-64069
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64069
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix cancellation of a DIO and single read subrequests

When the preparation of a new subrequest for a read fails, if the
subrequest has already been added to the stream->subrequests list, it can't
simply be put and abandoned as the collector may see it.  Also, if it
hasn't been queued yet, it has two outstanding refs that both need to be
put.  Both DIO read and single-read dispatch fail at this; further, both
differ in the order they do things to the way buffered read works.

Fix cancellation of both DIO-read and single-read subrequests that failed
preparation by the following steps:

 (1) Harmonise all three reads (buffered, dio, single) to queue the subreq
     before prepping it.

 (2) Make all three call netfs_queue_read() to do the queuing.

 (3) Set NETFS_RREQ_ALL_QUEUED independently of the queuing as we don't
     know the length of the subreq at this point.

 (4) In all cases, set the error and NETFS_SREQ_FAILED flag on the subreq
     and then call netfs_read_subreq_terminated() to deal with it.  This
     will pass responsibility off to the collector for dealing with it.

## References
- https://git.kernel.org/stable/c/5366199be46fb53de62861721d34ba816e7e440e
- https://git.kernel.org/stable/c/6f0f7ac1915abc0d202f0eb4b003a6548a5ba60d
- https://git.kernel.org/stable/c/f73372a4c6900d117f8e903fe10b62692f95e6c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64069.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
