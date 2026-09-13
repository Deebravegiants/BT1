# [H] fuse: re-lock request before replacing page cache folio

## Summary
Severity: High
Advisory: CVE-2026-53388
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53388
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14, >=7.1.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: re-lock request before replacing page cache folio

fuse_try_move_folio() unlocks the request on entry but does not
re-lock it on the success path. This means fuse_chan_abort() can end the
request and free the fuse_io_args (eg fuse_readpages_end()) while the
subsequent copy chain logic after fuse_try_move_folio() accesses the
fuse_io_args, leading to use-after-free issues.

Fix this by calling lock_request() before replace_page_cache_folio().
This ensures the request is locked on the success path which will
prevent the fuse_io_args from being freed while the later copying logic
runs, and also ensures that the ap->folios[i]->mapping is never null
since ap->folios[i] will always point to the newfolio after
replace_page_cache_folio().

## References
- https://git.kernel.org/stable/c/0223f452532d9cd8a5e87c45de828fd93c99bd25
- https://git.kernel.org/stable/c/030fe3e9d8abdee303dd7e9e42f45082d382a407
- https://git.kernel.org/stable/c/46473ddccdc5065033e397d6e62c280dbcd3d9c2
- https://git.kernel.org/stable/c/5927b43a4f8d89e86930f524bf63e9c7e66f61b4
- https://git.kernel.org/stable/c/7c18691e0cfda29672f79bafde8abdb7710674f6
- https://git.kernel.org/stable/c/a078484921052d0badd827fcc2770b5cfc1d4120
- https://git.kernel.org/stable/c/af2892249d982a1c036ca456cc135374e68b6677
- https://git.kernel.org/stable/c/e28db6ac4792d065ab32565fd9f0a2361c3d4666
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53388.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
