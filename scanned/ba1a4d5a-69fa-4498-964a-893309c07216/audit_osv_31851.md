# [H] btrfs: fix use-after-free on inode when scanning root during em shrinking

## Summary
Severity: High
Advisory: CVE-2025-21879
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21879
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix use-after-free on inode when scanning root during em shrinking

At btrfs_scan_root() we are accessing the inode's root (and fs_info) in a
call to btrfs_fs_closing() after we have scheduled the inode for a delayed
iput, and that can result in a use-after-free on the inode in case the
cleaner kthread does the iput before we dereference the inode in the call
to btrfs_fs_closing().

Fix this by using the fs_info stored already in a local variable instead
of doing inode->root->fs_info.

## References
- https://git.kernel.org/stable/c/07836bc18f4ae42da4e922244f4685561c18755e
- https://git.kernel.org/stable/c/59f37036bb7ab3d554c24abc856aabca01126414
- https://git.kernel.org/stable/c/5e79d26014f9386387575b9ed60d342057cee49b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21879.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21879
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
