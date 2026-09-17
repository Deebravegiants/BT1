# [H] CVE-2023-3111

## Summary
Severity: High
Advisory: CVE-2023-3111
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-05
Source: https://osv.dev/vulnerability/CVE-2023-3111
Type: osv

## Details
A use after free vulnerability was found in prepare_to_relocate in fs/btrfs/relocation.c in btrfs in the Linux Kernel. This possible flaw can be triggered by calling btrfs_ioctl_balance() before calling btrfs_ioctl_defrag().

## References
- https://patchwork.kernel.org/project/linux-btrfs/patch/20220721074829.2905233-1-r33s3n6%40gmail.com/
- https://security.netapp.com/advisory/ntap-20230703-0007/
- https://www.debian.org/security/2023/dsa-5480
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
