# [H] nilfs2: fix use-after-free bug of nilfs_root in nilfs_evict_inode()

## Summary
Severity: High
Advisory: CVE-2023-53804
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53804
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix use-after-free bug of nilfs_root in nilfs_evict_inode()

During unmount process of nilfs2, nothing holds nilfs_root structure after
nilfs2 detaches its writer in nilfs_detach_log_writer().  However, since
nilfs_evict_inode() uses nilfs_root for some cleanup operations, it may
cause use-after-free read if inodes are left in "garbage_list" and
released by nilfs_dispose_list() at the end of nilfs_detach_log_writer().

Fix this issue by modifying nilfs_evict_inode() to only clear inode
without additional metadata changes that use nilfs_root if the file system
is degraded to read-only or the writer is detached.

## References
- https://git.kernel.org/stable/c/116d53f09ff52e6f98e3fe1f85d8898d6ba26c68
- https://git.kernel.org/stable/c/2a782ea8ebd712a458466e3103e2881b4f886cb5
- https://git.kernel.org/stable/c/6b4205ea97901f822004e6c8d59484ccfda03faa
- https://git.kernel.org/stable/c/9b5a04ac3ad9898c4745cba46ea26de74ba56a8e
- https://git.kernel.org/stable/c/acc2a40e428f12780004e1e9fce4722d88f909fd
- https://git.kernel.org/stable/c/b8427b8522d9ede53015ba45a9978ba68d1162f5
- https://git.kernel.org/stable/c/f31e18131ee2ce80a4da5c808221d25b1ae9ad6d
- https://git.kernel.org/stable/c/fb8e8d58f116d069e5939e1f786ac84e7fa4533e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53804.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53804
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
