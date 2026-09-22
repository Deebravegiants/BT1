# [H] CVE-2021-41072

## Summary
Severity: High
Advisory: CVE-2021-41072
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-09-14
Source: https://osv.dev/vulnerability/CVE-2021-41072
Type: osv

## Details
squashfs_opendir in unsquash-2.c in Squashfs-Tools 4.5 allows Directory Traversal, a different vulnerability than CVE-2021-40153. A squashfs filesystem that has been crafted to include a symbolic link and then contents under the same filename in a filesystem can cause unsquashfs to first create the symbolic link pointing outside the expected directory, and then the subsequent write operation will cause the unsquashfs process to write through the symbolic link elsewhere in the filesystem.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00017.html
- https://security.gentoo.org/glsa/202305-29
- https://www.debian.org/security/2021/dsa-4987
- https://github.com/plougher/squashfs-tools/commit/e0485802ec72996c20026da320650d8362f555bd
- https://github.com/plougher/squashfs-tools/issues/72#issuecomment-913833405
