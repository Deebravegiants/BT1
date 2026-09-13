# [H] 9p: skip nlink update in cacheless mode to fix WARN_ON

## Summary
Severity: High
Advisory: CVE-2026-72170
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72170
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: skip nlink update in cacheless mode to fix WARN_ON

v9fs_dec_count() unconditionally calls drop_nlink() on regular files,
even when the inode's nlink is already zero. In cacheless mode the
client refetches inode metadata from the server (the source of truth)
on every operation, so by the time v9fs_remove() returns, the locally
cached nlink may already reflect the post-unlink value:

  1. Client initiates unlink, server processes it and sets nlink to 0
  2. Client refetches inode metadata (nlink=0) before unlink returns
  3. Client's v9fs_remove() completes successfully
  4. Client calls v9fs_dec_count() which calls drop_nlink() on nlink=0

This race is easily triggered under heavy unlink workloads, such as
stress-ng's unlink stressor, producing the following warning:

  WARNING: fs/inode.c:417 at drop_nlink+0x4c/0xc8
  Call trace:
   drop_nlink+0x4c/0xc8
   v9fs_remove+0x1e0/0x250 [9p]
   v9fs_vfs_unlink+0x20/0x38 [9p]
   vfs_unlink+0x13c/0x258
   ...

In cacheless mode the server is authoritative and the inode is on its
way out, so locally adjusting nlink buys nothing. Skip v9fs_dec_count()
entirely when neither CACHE_META nor CACHE_LOOSE is set, which both
avoids the warning and removes a class of nlink races (two concurrent
unlinkers observing nlink > 0 and both calling drop_nlink()) that an
nlink == 0 guard alone would only narrow rather than close.

## References
- https://git.kernel.org/stable/c/4ec4ebe40c82cb4c60756732f6593055d010c59c
- https://git.kernel.org/stable/c/574aa0b4799470ac814479f1138d19efe6262255
- https://git.kernel.org/stable/c/6086469f7d469549bfd070348b717a6e43736200
- https://git.kernel.org/stable/c/8d610017c992de705b304d3d727a6e3a86af6149
- https://git.kernel.org/stable/c/8faccac11e1369adddf5d80f4a45af93f13b2e1a
- https://git.kernel.org/stable/c/a5a682b016ef5b5384e28f6d652d47a8f8e73d37
- https://git.kernel.org/stable/c/ab257019cb72f467b55c95384d99c94e3908b928
- https://git.kernel.org/stable/c/de79c3f3643841b8659a71958df7cf2a66bfd409
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72170.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
