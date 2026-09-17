# [H] ocfs2: fix crash when mount with quota enabled

## Summary
Severity: High
Advisory: CVE-2022-49274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49274
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix crash when mount with quota enabled

There is a reported crash when mounting ocfs2 with quota enabled.

  RIP: 0010:ocfs2_qinfo_lock_res_init+0x44/0x50 [ocfs2]
  Call Trace:
    ocfs2_local_read_info+0xb9/0x6f0 [ocfs2]
    dquot_load_quota_sb+0x216/0x470
    dquot_load_quota_inode+0x85/0x100
    ocfs2_enable_quotas+0xa0/0x1c0 [ocfs2]
    ocfs2_fill_super.cold+0xc8/0x1bf [ocfs2]
    mount_bdev+0x185/0x1b0
    legacy_get_tree+0x27/0x40
    vfs_get_tree+0x25/0xb0
    path_mount+0x465/0xac0
    __x64_sys_mount+0x103/0x140

It is caused by when initializing dqi_gqlock, the corresponding dqi_type
and dqi_sb are not properly initialized.

This issue is introduced by commit 6c85c2c72819, which wants to avoid
accessing uninitialized variables in error cases.  So make global quota
info properly initialized.

## References
- https://git.kernel.org/stable/c/01931e1c4e3de5d777253acae64c0e8fd071a1dd
- https://git.kernel.org/stable/c/7c5312fdb1dcfdc1951b018669af88d5d6420b31
- https://git.kernel.org/stable/c/de19433423c7bedabbd4f9a25f7dbc62c5e78921
- https://git.kernel.org/stable/c/eda31f77317647b9fbf889779ee1fb6907651865
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49274.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
