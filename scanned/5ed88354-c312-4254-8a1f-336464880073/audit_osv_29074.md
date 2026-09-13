# [H] 9p: add missing locking around taking dentry fid list

## Summary
Severity: High
Advisory: CVE-2024-39463
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39463
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.168, >=5.16.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: add missing locking around taking dentry fid list

Fix a use-after-free on dentry's d_fsdata fid list when a thread
looks up a fid through dentry while another thread unlinks it:

UAF thread:
refcount_t: addition on 0; use-after-free.
 p9_fid_get linux/./include/net/9p/client.h:262
 v9fs_fid_find+0x236/0x280 linux/fs/9p/fid.c:129
 v9fs_fid_lookup_with_uid linux/fs/9p/fid.c:181
 v9fs_fid_lookup+0xbf/0xc20 linux/fs/9p/fid.c:314
 v9fs_vfs_getattr_dotl+0xf9/0x360 linux/fs/9p/vfs_inode_dotl.c:400
 vfs_statx+0xdd/0x4d0 linux/fs/stat.c:248

Freed by:
 p9_fid_destroy (inlined)
 p9_client_clunk+0xb0/0xe0 linux/net/9p/client.c:1456
 p9_fid_put linux/./include/net/9p/client.h:278
 v9fs_dentry_release+0xb5/0x140 linux/fs/9p/vfs_dentry.c:55
 v9fs_remove+0x38f/0x620 linux/fs/9p/vfs_inode.c:518
 vfs_unlink+0x29a/0x810 linux/fs/namei.c:4335

The problem is that d_fsdata was not accessed under d_lock, because
d_release() normally is only called once the dentry is otherwise no
longer accessible but since we also call it explicitly in v9fs_remove
that lock is required:
move the hlist out of the dentry under lock then unref its fids once
they are no longer accessible.

## References
- https://git.kernel.org/stable/c/3bb6763a8319170c2d41c4232c8e7e4c37dcacfb
- https://git.kernel.org/stable/c/c898afdc15645efb555acb6d85b484eb40a45409
- https://git.kernel.org/stable/c/cb299cdba09f46f090b843d78ba26b667d50a456
- https://git.kernel.org/stable/c/f0c5c944c6d8614c19e6e9a97fd2011dcd30e8f5
- https://git.kernel.org/stable/c/fe17ebf22feb4ad7094d597526d558a49aac92b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39463.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39463
- https://www.zerodayinitiative.com/advisories/ZDI-24-1194/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
