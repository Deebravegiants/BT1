# [H] spufs: fix gang directory lifetimes

## Summary
Severity: High
Advisory: CVE-2025-22072
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22072
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

spufs: fix gang directory lifetimes

prior to "[POWERPC] spufs: Fix gang destroy leaks" we used to have
a problem with gang lifetimes - creation of a gang returns opened
gang directory, which normally gets removed when that gets closed,
but if somebody has created a context belonging to that gang and
kept it alive until the gang got closed, removal failed and we
ended up with a leak.

Unfortunately, it had been fixed the wrong way.  Dentry of gang
directory was no longer pinned, and rmdir on close was gone.
One problem was that failure of open kept calling simple_rmdir()
as cleanup, which meant an unbalanced dput().  Another bug was
in the success case - gang creation incremented link count on
root directory, but that was no longer undone when gang got
destroyed.

Fix consists of
	* reverting the commit in question
	* adding a counter to gang, protected by ->i_rwsem
of gang directory inode.
	* having it set to 1 at creation time, dropped
in both spufs_dir_close() and spufs_gang_close() and bumped
in spufs_create_context(), provided that it's not 0.
	* using simple_recursive_removal() to take the gang
directory out when counter reaches zero.

## References
- https://git.kernel.org/stable/c/029d8c711f5e5fe8cf63e8a4a1a140a06e224e45
- https://git.kernel.org/stable/c/324f280806aab28ef757aecc18df419676c10ef8
- https://git.kernel.org/stable/c/880e7b3da2e765c1f90c94c0539be039e96c7062
- https://git.kernel.org/stable/c/903733782f3ae28a2f7fe4dfb47c7fe3e079a528
- https://git.kernel.org/stable/c/c134deabf4784e155d360744d4a6a835b9de4dd4
- https://git.kernel.org/stable/c/fc646a6c6d14b5d581f162a7e32999f789e3a3ac
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22072.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
