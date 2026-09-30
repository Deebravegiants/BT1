# [H] fuse: revert back to __readahead_folio() for readahead

## Summary
Severity: High
Advisory: CVE-2025-21896
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21896
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: revert back to __readahead_folio() for readahead

In commit 3eab9d7bc2f4 ("fuse: convert readahead to use folios"), the
logic was converted to using the new folio readahead code, which drops
the reference on the folio once it is locked, using an inferred
reference on the folio. Previously we held a reference on the folio for
the entire duration of the readpages call.

This is fine, however for the case for splice pipe responses where we
will remove the old folio and splice in the new folio (see
fuse_try_move_page()), we assume that there is a reference held on the
folio for ap->folios, which is no longer the case.

To fix this, revert back to __readahead_folio() which allows us to hold
the reference on the folio for the duration of readpages until either we
drop the reference ourselves in fuse_readpages_end() or the reference is
dropped after it's replaced in the page cache in the splice case.
This will fix the UAF bug that was reported.

## References
- https://git.kernel.org/stable/c/0c67c37e1710b2a8f61c8a02db95a51fe577e2c1
- https://git.kernel.org/stable/c/60db11f1b7fba4a66b117ea998d965818784a98d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21896.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21896
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
