# [M] btrfs: fix race between quota enable and quota rescan ioctl

## Summary
Severity: Medium
Advisory: CVE-2022-50379
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50379
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix race between quota enable and quota rescan ioctl

When enabling quotas, at btrfs_quota_enable(), after committing the
transaction, we change fs_info->quota_root to point to the quota root we
created and set BTRFS_FS_QUOTA_ENABLED at fs_info->flags. Then we try
to start the qgroup rescan worker, first by initializing it with a call
to qgroup_rescan_init() - however if that fails we end up freeing the
quota root but we leave fs_info->quota_root still pointing to it, this
can later result in a use-after-free somewhere else.

We have previously set the flags BTRFS_FS_QUOTA_ENABLED and
BTRFS_QGROUP_STATUS_FLAG_ON, so we can only fail with -EINPROGRESS at
btrfs_quota_enable(), which is possible if someone already called the
quota rescan ioctl, and therefore started the rescan worker.

So fix this by ignoring an -EINPROGRESS and asserting we can't get any
other error.

## References
- https://git.kernel.org/stable/c/0efd9dfc00d677a1d0929319a6103cb2dfc41c22
- https://git.kernel.org/stable/c/26b7c0ac49a3eea15559c9d84863736a6d1164b4
- https://git.kernel.org/stable/c/331cd9461412e103d07595a10289de90004ac890
- https://git.kernel.org/stable/c/47b5ffe86332af95f0f52be0a63d4da7c2b37b55
- https://git.kernel.org/stable/c/4b996a3014ef014af8f97b60c35f5289210a4720
- https://git.kernel.org/stable/c/6c22f86dd221eba0c7af645b1af73dcbc04ee27b
- https://git.kernel.org/stable/c/c97f6d528c3f1c83a6b792a8a7928c236c80b8fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50379.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50379
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
