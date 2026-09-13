# [M] ext4: don't set SB_RDONLY after filesystem errors

## Summary
Severity: Medium
Advisory: CVE-2024-50191
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50191
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: don't set SB_RDONLY after filesystem errors

When the filesystem is mounted with errors=remount-ro, we were setting
SB_RDONLY flag to stop all filesystem modifications. We knew this misses
proper locking (sb->s_umount) and does not go through proper filesystem
remount procedure but it has been the way this worked since early ext2
days and it was good enough for catastrophic situation damage
mitigation. Recently, syzbot has found a way (see link) to trigger
warnings in filesystem freezing because the code got confused by
SB_RDONLY changing under its hands. Since these days we set
EXT4_FLAGS_SHUTDOWN on the superblock which is enough to stop all
filesystem modifications, modifying SB_RDONLY shouldn't be needed. So
stop doing that.

## References
- https://git.kernel.org/stable/c/58c0648e4c773f5b54f0cb63bc8c7c6bf52719a9
- https://git.kernel.org/stable/c/d3476f3dad4ad68ae5f6b008ea6591d1520da5d8
- https://git.kernel.org/stable/c/ee77c388469116565e009eaa704a60bc78489e09
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50191.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50191
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
