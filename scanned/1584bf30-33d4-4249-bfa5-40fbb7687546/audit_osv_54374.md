# [M] CVE-2023-52429

## Summary
Severity: Medium
Advisory: CVE-2023-52429
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-12
Source: https://osv.dev/vulnerability/CVE-2023-52429
Type: osv

## Details
dm_table_create in drivers/md/dm-table.c in the Linux kernel through 6.7.4 can attempt to (in alloc_targets) allocate more than INT_MAX bytes, and crash, because of a missing check for struct dm_ioctl.target_count.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3LZROQAX7Q7LEP4F7WQ3KUZKWCZGFFP2/
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GS7S3XLTLOUKBXV67LLFZWB3YVFJZHRK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3LZROQAX7Q7LEP4F7WQ3KUZKWCZGFFP2/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=bd504bcfec41a503b32054da5472904b404341a4
- https://www.spinics.net/lists/dm-devel/msg56625.html
