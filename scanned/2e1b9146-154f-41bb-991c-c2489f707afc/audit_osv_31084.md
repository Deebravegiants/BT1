# [M] nfs: Fix oops in nfs_netfs_init_request() when copying to cache

## Summary
Severity: Medium
Advisory: CVE-2024-57927
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57927
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs: Fix oops in nfs_netfs_init_request() when copying to cache

When netfslib wants to copy some data that has just been read on behalf of
nfs, it creates a new write request and calls nfs_netfs_init_request() to
initialise it, but with a NULL file pointer.  This causes
nfs_file_open_context() to oops - however, we don't actually need the nfs
context as we're only going to write to the cache.

Fix this by just returning if we aren't given a file pointer and emit a
warning if the request was for something other than copy-to-cache.

Further, fix nfs_netfs_free_request() so that it doesn't try to free the
context if the pointer is NULL.

## References
- https://git.kernel.org/stable/c/13a07cc81e2d116cece727a83746c74b87a9d417
- https://git.kernel.org/stable/c/86ad1a58f6a9453f49e06ef957a40a8dac00a13f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57927.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
