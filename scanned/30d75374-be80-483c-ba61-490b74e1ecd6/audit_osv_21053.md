# [H] CVE-2021-40153

## Summary
Severity: High
Advisory: CVE-2021-40153
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-40153
Type: osv

## Details
squashfs_opendir in unsquash-1.c in Squashfs-Tools 4.5 stores the filename in the directory entry; this is then used by unsquashfs to create the new file during the unsquash. The filename is not validated for traversal outside of the destination directory, and thus allows writing to locations outside of the destination.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GSMRKVJMJFX3MB7D3PXJSYY3TLZROE5S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RAOZ4BKWAC4Y3U2K5MMW3S77HWWXHQDL/
- https://bugs.launchpad.net/ubuntu/+source/squashfs-tools/+bug/1941790
- https://lists.debian.org/debian-lts-announce/2021/08/msg00030.html
- https://security.gentoo.org/glsa/202305-29
- https://www.debian.org/security/2021/dsa-4967
- https://github.com/plougher/squashfs-tools/commit/79b5a555058eef4e1e7ff220c344d39f8cd09646
- https://github.com/plougher/squashfs-tools/issues/72
