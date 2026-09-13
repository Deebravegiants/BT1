# [H] afs: Fix the locking used by afs_get_link()

## Summary
Severity: High
Advisory: CVE-2026-64057
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64057
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix the locking used by afs_get_link()

The afs filesystem in the kernel doesn't do locking correctly for symbolic
links.  There are a number of problems:

 (1) It doesn't do any locking around afs_read_single() to prevent races
     between multiple ->get_link() calls, thereby allowing the possibility
     of leaks.

 (2) It doesn't use RCU barriering when accessing the buffer pointers
     during RCU pathwalk.

 (3) It can race with another thread updating the contents of the symlink
     if a third party updated it on the server.

Fix this by the following means:

 (0) Move symlink handling into its own file as this makes it more
     complicated.

 (1) Take the validate_lock around afs_read_single() to prevent races
     between multiple ->get_link() calls.

 (2) Keep a separate copy of the symlink contents with an rcu_head.  This
     is always going to be a lot smaller than a page, so it can be
     kmalloc'd and save quite a bit of memory.  It also needs a refcount
     for non-RCU pathwalk.

 (3) Split the symlink read and write-to-cache routines in afs from those
     for directories.

 (4) Discard the I/O buffer as soon as the write-to-cache completes as this
     is a full page (plus a folio_queue).

 (5) If there's no cache, discard the I/O buffer immediately after reading
     and copying if there is no cache.

## References
- https://git.kernel.org/stable/c/77ea917cbed62882a33114b1e23ededb977e4287
- https://git.kernel.org/stable/c/c0410adf3da6db46f3513411fcf95e63c2f1d1ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64057.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
