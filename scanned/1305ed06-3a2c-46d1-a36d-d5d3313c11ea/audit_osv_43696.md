# [C] mm/filemap: __filemap_add_folio() restore index before retrying

## Summary
Severity: Critical
Advisory: CVE-2026-74591
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74591
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/filemap: __filemap_add_folio() restore index before retrying

In __filemap_add_folio()'s split-a-conflict loop, xas_set_order() is
applied repeatedly: each application modifies xas.xa_index, rounding it
down according to the split_order attempted at that stage: and if all goes
as intended, it eventually (or immediately) converges on an
xas_try_split() to the required folio_order, with xas.xa_index now the
same as index: then xas_store() puts the new folio into the xarray there.

But if a new node was needed, and GFP_NOWAIT allocation did not get one,
the lock is dropped, xas_nomem() used to allocate, and sequence retried. 
If (that part of) the xarray is unchanged when the lock is reacquired, no
problem.  But what if the conflict was meanwhile resolved by another
thread (perhaps even doing the same thing, inserting a folio at that same
index)?  Isn't there a danger of now putting our folio into the xarray at
an intermediate rounded-down index?  With !folio_contains() bug to follow,
when CONFIG_DEBUG_VM=y is checking for that.

Fix this with an xas_set_order() to restore the original xas.xa_index at
the bottom of the loop, so the retry does a full re-evaluation after
reacquiring the lock, and cannot reach xas_store() with the wrong index.

Production was suffering from rare SIGILLs and SIGSEGVs, executable text
found a page away from where it belonged, !folio_contains() bug hit when
debug enabled: symptoms not seen since this patch went in.

## References
- https://git.kernel.org/stable/c/267ecd2eb7759c26f1a026eb0a5b231071534c9c
- https://git.kernel.org/stable/c/4917e3ebcab50f0265e8ca01c8567de4c4a47511
- https://git.kernel.org/stable/c/86da3f7e1e609e1e8bfbab198af68467c5a015a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74591.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74591
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
