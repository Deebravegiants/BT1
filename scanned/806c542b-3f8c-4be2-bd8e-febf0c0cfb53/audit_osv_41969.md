# [C] netfs: Fix potential UAF in netfs_unlock_abandoned_read_pages()

## Summary
Severity: Critical
Advisory: CVE-2026-64216
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64216
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.106, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix potential UAF in netfs_unlock_abandoned_read_pages()

netfs_unlock_abandoned_read_pages(rreq) accesses the index of the folios it
is wanting to unlock and compares that to rreq->no_unlock_folio so that it
doesn't unlock a folio being read for netfs_perform_write() or
netfs_write_begin().

However, given that netfs_unlock_abandoned_read_pages() is called _after_
NETFS_RREQ_IN_PROGRESS is cleared, the one folio that it's not allowed to
dereference is the one specified by ->no_unlock_folio as ownership
immediately reverts to the caller.

Fix this by storing the folio pointer instead and using that rather than
the index.  Also fix netfs_unlock_read_folio() where the same applies.

## References
- https://git.kernel.org/stable/c/3866d015f33aeedf81338dd99154703bef33faef
- https://git.kernel.org/stable/c/6080fa3ecfbb4448a3b47368629534c09b6ec750
- https://git.kernel.org/stable/c/d4ae8dba90b89e7bb4d1045d1cb26afbaf13ee5c
- https://git.kernel.org/stable/c/dbe556972100fabb8e5a1b3d2163831ff07b1e8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64216.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64216
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
