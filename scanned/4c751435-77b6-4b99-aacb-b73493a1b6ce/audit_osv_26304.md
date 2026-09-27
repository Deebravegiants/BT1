# [M] fs: Pass AT_GETATTR_NOSEC flag to getattr interface function

## Summary
Severity: Medium
Advisory: CVE-2023-52779
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52779
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: Pass AT_GETATTR_NOSEC flag to getattr interface function

When vfs_getattr_nosec() calls a filesystem's getattr interface function
then the 'nosec' should propagate into this function so that
vfs_getattr_nosec() can again be called from the filesystem's gettattr
rather than vfs_getattr(). The latter would add unnecessary security
checks that the initial vfs_getattr_nosec() call wanted to avoid.
Therefore, introduce the getattr flag GETATTR_NOSEC and allow to pass
with the new getattr_flags parameter to the getattr interface function.
In overlayfs and ecryptfs use this flag to determine which one of the
two functions to call.

In a recent code change introduced to IMA vfs_getattr_nosec() ended up
calling vfs_getattr() in overlayfs, which in turn called
security_inode_getattr() on an exiting process that did not have
current->fs set anymore, which then caused a kernel NULL pointer
dereference. With this change the call to security_inode_getattr() can
be avoided, thus avoiding the NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/3fb0fa08641903304b9d81d52a379ff031dc41d4
- https://git.kernel.org/stable/c/8a924db2d7b5eb69ba08b1a0af46e9f1359a9bdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52779.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52779
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
