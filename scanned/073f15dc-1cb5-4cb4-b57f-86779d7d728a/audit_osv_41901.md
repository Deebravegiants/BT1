# [C] netfs: Fix missing barriers when accessing stream->subrequests locklessly

## Summary
Severity: Critical
Advisory: CVE-2026-64067
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64067
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix missing barriers when accessing stream->subrequests locklessly

The list of subrequests attached to stream->subrequests is accessed without
locks by netfs_collect_read_results() and netfs_collect_write_results(),
and then they access subreq->flags without taking a barrier after getting
the subreq pointer from the list.  Relatedly, the functions that build the
list don't use any sort of write barrier when constructing the list to make
sure that the NETFS_SREQ_IN_PROGRESS flag is perceived to be set first if
no lock is taken.

Fix this by:

 (1) Add a new list_add_tail_release() function that uses a release barrier
     to set the pointer to the new member of the list.

 (2) Add a new list_first_entry_or_null_acquire() function that uses an
     acquire barrier to read the pointer to the first member in a list (or
     return NULL).

 (3) Use list_add_tail_release() when adding a subreq to ->subrequests.

 (4) Use list_first_entry_or_null_acquire() when initially accessing the
     front of the list (when an item is removed, the pointer to the new
     front iterm is obtained under the same lock).

## References
- https://git.kernel.org/stable/c/293a4532c36f38458e38b8879b174ab797718b9d
- https://git.kernel.org/stable/c/b5782e2d462c028096f922abca46318cec890670
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64067.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64067
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
