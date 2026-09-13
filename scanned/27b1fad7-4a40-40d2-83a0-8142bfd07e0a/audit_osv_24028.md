# [M] capabilities: fix potential memleak on error path from vfs_getxattr_alloc()

## Summary
Severity: Medium
Advisory: CVE-2022-49890
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49890
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

capabilities: fix potential memleak on error path from vfs_getxattr_alloc()

In cap_inode_getsecurity(), we will use vfs_getxattr_alloc() to
complete the memory allocation of tmpbuf, if we have completed
the memory allocation of tmpbuf, but failed to call handler->get(...),
there will be a memleak in below logic:

  |-- ret = (int)vfs_getxattr_alloc(mnt_userns, ...)
    |           /* ^^^ alloc for tmpbuf */
    |-- value = krealloc(*xattr_value, error + 1, flags)
    |           /* ^^^ alloc memory */
    |-- error = handler->get(handler, ...)
    |           /* error! */
    |-- *xattr_value = value
    |           /* xattr_value is &tmpbuf (memory leak!) */

So we will try to free(tmpbuf) after vfs_getxattr_alloc() fails to fix it.

[PM: subject line and backtrace tweaks]

## References
- https://git.kernel.org/stable/c/0c3e6288da650d1ec911a259c77bc2d88e498603
- https://git.kernel.org/stable/c/2de8eec8afb75792440b8900a01d52b8f6742fd1
- https://git.kernel.org/stable/c/6bb00eb21c0fbf18e5d3538c9ff0cf63fd0ace85
- https://git.kernel.org/stable/c/7480aeff0093d8c54377553ec6b31110bea37b4d
- https://git.kernel.org/stable/c/8cf0a1bc12870d148ae830a4ba88cfdf0e879cee
- https://git.kernel.org/stable/c/90577bcc01c4188416a47269f8433f70502abe98
- https://git.kernel.org/stable/c/cdf01c807e974048c43c7fd3ca574f6086a57906
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49890.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49890
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
