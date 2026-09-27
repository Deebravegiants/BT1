# [M] btrfs: add a sanity check for btrfs root in btrfs_search_slot()

## Summary
Severity: Medium
Advisory: CVE-2024-56774
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56774
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: add a sanity check for btrfs root in btrfs_search_slot()

Syzbot reports a null-ptr-deref in btrfs_search_slot().

The reproducer is using rescue=ibadroots, and the extent tree root is
corrupted thus the extent tree is NULL.

When scrub tries to search the extent tree to gather the needed extent
info, btrfs_search_slot() doesn't check if the target root is NULL or
not, resulting the null-ptr-deref.

Add sanity check for btrfs root before using it in btrfs_search_slot().

## References
- https://git.kernel.org/stable/c/3ed51857a50f530ac7a1482e069dfbd1298558d4
- https://git.kernel.org/stable/c/757171d1369b3b47f36932d40a05a0715496dcab
- https://git.kernel.org/stable/c/93992c3d9629b02dccf6849238559d5c24f2dece
- https://git.kernel.org/stable/c/c71d114ef68c95da5a82ec85a721ab31f5bd905b
- https://git.kernel.org/stable/c/db66fb87c21e8ae724886e6a464dcbac562a64c6
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56774.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56774
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
