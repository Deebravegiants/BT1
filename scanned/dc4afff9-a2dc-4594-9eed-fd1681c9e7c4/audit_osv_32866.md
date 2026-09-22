# [H] erofs: avoid using multiple devices with different type

## Summary
Severity: High
Advisory: CVE-2025-38172
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38172
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: avoid using multiple devices with different type

For multiple devices, both primary and extra devices should be the
same type. `erofs_init_device` has already guaranteed that if the
primary is a file-backed device, extra devices should also be
regular files.

However, if the primary is a block device while the extra device
is a file-backed device, `erofs_init_device` will get an ENOTBLK,
which is not treated as an error in `erofs_fc_get_tree`, and that
leads to an UAF:

  erofs_fc_get_tree
    get_tree_bdev_flags(erofs_fc_fill_super)
      erofs_read_superblock
        erofs_init_device  // sbi->dif0 is not inited yet,
                           // return -ENOTBLK
      deactivate_locked_super
        free(sbi)
    if (err is -ENOTBLK)
      sbi->dif0.file = filp_open()  // sbi UAF

So if -ENOTBLK is hitted in `erofs_init_device`, it means the
primary device must be a block device, and the extra device
is not a block device. The error can be converted to -EINVAL.

## References
- https://git.kernel.org/stable/c/65115472f741ca000d7ea4a5922214f93cd1516e
- https://git.kernel.org/stable/c/9748f2f54f66743ac77275c34886a9f890e18409
- https://git.kernel.org/stable/c/cd04beb9ce2773a16057248bb4fa424068ae3807
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38172.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
