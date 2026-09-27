# [M] CVE-2023-1611

## Summary
Severity: Medium
Advisory: CVE-2023-1611
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-04-03
Source: https://osv.dev/vulnerability/CVE-2023-1611
Type: osv

## Details
A use-after-free flaw was found in btrfs_search_slot in fs/btrfs/ctree.c in btrfs in the Linux Kernel.This flaw allows an attacker to crash the system and possibly cause a kernel information lea

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5QCM6XO4HSPLGR3DFYWFRIA3GCBIHZR4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZWECAZ7V7EPSXMINO6Q6KWNKDY2CO6ZW/
- https://lore.kernel.org/linux-btrfs/35b9a70650ea947387cf352914a8774b4f7e8a6f.1679481128.git.fdmanana%40suse.com/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2181342
- https://github.com/torvalds/linux/commit/2f1a6be12ab6c8470d5776e68644726c94257c54
