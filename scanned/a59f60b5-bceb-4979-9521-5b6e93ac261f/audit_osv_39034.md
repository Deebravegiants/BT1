# [H] ceph: add a bunch of missing ceph_path_info initializers

## Summary
Severity: High
Advisory: CVE-2026-43408
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43408
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.78, >=6.13.0 <6.18.19, >=6.17.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: add a bunch of missing ceph_path_info initializers

ceph_mdsc_build_path() must be called with a zero-initialized
ceph_path_info parameter, or else the following
ceph_mdsc_free_path_info() may crash.

Example crash (on Linux 6.18.12):

  virt_to_cache: Object is not a Slab page!
  WARNING: CPU: 184 PID: 2871736 at mm/slub.c:6732 kmem_cache_free+0x316/0x400
  [...]
  Call Trace:
   [...]
   ceph_open+0x13d/0x3e0
   do_dentry_open+0x134/0x480
   vfs_open+0x2a/0xe0
   path_openat+0x9a3/0x1160
  [...]
  cache_from_obj: Wrong slab cache. names_cache but object is from ceph_inode_info
  WARNING: CPU: 184 PID: 2871736 at mm/slub.c:6746 kmem_cache_free+0x2dd/0x400
  [...]
  kernel BUG at mm/slub.c:634!
  Oops: invalid opcode: 0000 [#1] SMP NOPTI
  RIP: 0010:__slab_free+0x1a4/0x350

Some of the ceph_mdsc_build_path() callers had initializers, but
others had not, even though they were all added by commit 15f519e9f883
("ceph: fix race condition validating r_parent before applying state").
The ones without initializer are suspectible to random crashes.  (I can
imagine it could even be possible to exploit this bug to elevate
privileges.)

Unfortunately, these Ceph functions are undocumented and its semantics
can only be derived from the code.  I see that ceph_mdsc_build_path()
initializes the structure only on success, but not on error.

Calling ceph_mdsc_free_path_info() after a failed
ceph_mdsc_build_path() call does not even make sense, but that's what
all callers do, and for it to be safe, the structure must be
zero-initialized.  The least intrusive approach to fix this is
therefore to add initializers everywhere.

## References
- https://git.kernel.org/stable/c/43323a5934b660afae687e8e4e95ac328615a5c4
- https://git.kernel.org/stable/c/453df1f4535842bf17ff1885a225e153d7ee3374
- https://git.kernel.org/stable/c/644b47f0574fd82aeb9d00317eca8d1f2a525c8c
- https://git.kernel.org/stable/c/8be8911f590813e6f90bc6407ced1b23e50bc5da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43408.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
