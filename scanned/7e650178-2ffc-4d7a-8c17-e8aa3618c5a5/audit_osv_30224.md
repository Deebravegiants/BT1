# [M] nilfs2: propagate directory read errors from nilfs_find_entry()

## Summary
Severity: Medium
Advisory: CVE-2024-50202
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50202
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: propagate directory read errors from nilfs_find_entry()

Syzbot reported that a task hang occurs in vcs_open() during a fuzzing
test for nilfs2.

The root cause of this problem is that in nilfs_find_entry(), which
searches for directory entries, ignores errors when loading a directory
page/folio via nilfs_get_folio() fails.

If the filesystem images is corrupted, and the i_size of the directory
inode is large, and the directory page/folio is successfully read but
fails the sanity check, for example when it is zero-filled,
nilfs_check_folio() may continue to spit out error messages in bursts.

Fix this issue by propagating the error to the callers when loading a
page/folio fails in nilfs_find_entry().

The current interface of nilfs_find_entry() and its callers is outdated
and cannot propagate error codes such as -EIO and -ENOMEM returned via
nilfs_find_entry(), so fix it together.

## References
- https://git.kernel.org/stable/c/08cfa12adf888db98879dbd735bc741360a34168
- https://git.kernel.org/stable/c/270a6f9df35fa2aea01ec23770dc9b3fc9a12989
- https://git.kernel.org/stable/c/9698088ac7704e260f492d9c254e29ed7dd8729a
- https://git.kernel.org/stable/c/b4b3dc9e7e604be98a222e9f941f5e93798ca475
- https://git.kernel.org/stable/c/bb857ae1efd3138c653239ed1e7aef14e1242c81
- https://git.kernel.org/stable/c/c1d0476885d708a932980b0f28cd90d9bd71db39
- https://git.kernel.org/stable/c/edf8146057264191d5bfe5b91773f13d936dadd3
- https://git.kernel.org/stable/c/efa810b15a25531cbc2f527330947b9fe16916e7
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50202.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
