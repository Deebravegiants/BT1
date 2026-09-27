# [M] CVE-2024-23850

## Summary
Severity: Medium
Advisory: CVE-2024-23850
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-23850
Type: osv

## Details
In btrfs_get_root_ref in fs/btrfs/disk-io.c in the Linux kernel through 6.7.1, there can be an assertion failure and crash because a subvolume can be read out too soon after its root item is inserted upon subvolume creation.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://lore.kernel.org/all/6a80cb4b32af89787dadee728310e5e2ca85343f.1705741883.git.wqu%40suse.com/
- https://lore.kernel.org/lkml/CALGdzuo6awWdau3X=8XK547x2vX_-VoFmH1aPsqosRTQ5WzJVA%40mail.gmail.com/
