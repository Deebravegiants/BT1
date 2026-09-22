# [C] btrfs: tracepoints: get correct superblock from dentry in event btrfs_sync_file()

## Summary
Severity: Critical
Advisory: CVE-2026-43117
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43117
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: tracepoints: get correct superblock from dentry in event btrfs_sync_file()

If overlay is used on top of btrfs, dentry->d_sb translates to overlay's
super block and fsid assignment will lead to a crash.

Use file_inode(file)->i_sb to always get btrfs_sb.

## References
- https://git.kernel.org/stable/c/2e4adfaec97ee053ad1bdfb5036845e66f7e0d8a
- https://git.kernel.org/stable/c/32372781d664a9b03c40343e96c29d0a6139f97d
- https://git.kernel.org/stable/c/4a7bab35fad5251c8cb738161152578cd83b6b9c
- https://git.kernel.org/stable/c/520e8b4bcf872a534a7bf61ccf880047642df296
- https://git.kernel.org/stable/c/a85b46db143fda5869e7d8df8f258ccef5fa1719
- https://git.kernel.org/stable/c/c09a7446aab5773f38d6abb25fce99b8e1dfbc97
- https://git.kernel.org/stable/c/d110d7cdb045715c0b45b0dfd974525bb38f653d
- https://git.kernel.org/stable/c/e252db8ca2a01f82d472091f35d549b313278636
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
