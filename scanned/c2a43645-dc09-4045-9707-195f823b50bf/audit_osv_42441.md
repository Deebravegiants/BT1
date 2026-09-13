# [H] fs: preserve ACL_DONT_CACHE state in forget_cached_acl()

## Summary
Severity: High
Advisory: CVE-2026-68149
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68149
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: preserve ACL_DONT_CACHE state in forget_cached_acl()

The ACL_DONT_CACHE state is meant to be a constant state for the inode
for filesystems that want to opt out of posix acl caching.

Commit facd61053cff1 ("fuse: fixes after adapting to new posix acl api")
used this facility to opt out of posix acl caching for fuse inodes with
fuse server that does not negotiate FUSE_POSIX_ACL (fc->posix_acl).

The commit also takes care to gate the forget_all_cached_acls() call in
fuse_set_acl() on fc->posix_acl because there is no need for it, but
there are other placed in fuse code which call forget_all_cached_acls()
unconditional to fc->posix_acl and those cause the loss of the
ACL_DONT_CACHE state.

This is not only a functional bug. Properly timed, a get_acl() from this
fuse filesystem can return a stale cached value, as was observed in tests,
because set_acl() does not invalidate the unintentional acl cache.

We could fix this in fuse, but it actually makes no sense for the vfs
helper forget_cached_acl() to invalidate the ACL_DONT_CACHE state, so
let it not do that to fix fuse and future users of ACL_DONT_CACHE.

## References
- https://git.kernel.org/stable/c/4b9a5458d02e214ef2b384124ca626e3e381d778
- https://git.kernel.org/stable/c/834ddf899484a2f23129080e8773bc04f4691d07
- https://git.kernel.org/stable/c/a019b074903b3ad0a9726087efd0e8291452023b
- https://git.kernel.org/stable/c/b98fad81f1202b0eb26aacf3ff4cc7a21ed3b5bf
- https://git.kernel.org/stable/c/ca03a7984a34f48085fd013e0d2cf4e6420b4acf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68149.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
