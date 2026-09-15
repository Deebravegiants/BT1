# [M] CVE-2024-23849

## Summary
Severity: Medium
Advisory: CVE-2024-23849
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-23849
Type: osv

## Details
In rds_recv_track_latency in net/rds/af_rds.c in the Linux kernel through 6.7.1, there is an off-by-one error for an RDS_MSG_RX_DGRAM_TRACE_MAX comparison, resulting in out-of-bounds access.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7LSPIOMIJYTLZB6QKPQVVAYSUETUWKPF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBVHM4LGMFIHBN4UBESYRFMYX3WUICV5/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=13e788deb7348cc88df34bed736c3b3b9927ea52
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LBVHM4LGMFIHBN4UBESYRFMYX3WUICV5/
- https://lore.kernel.org/netdev/1705715319-19199-1-git-send-email-sharath.srinivasan%40oracle.com/
- https://lore.kernel.org/netdev/CALGdzuoVdq-wtQ4Az9iottBqC5cv9ZhcE5q8N7LfYFvkRsOVcw%40mail.gmail.com
- https://bugzilla.suse.com/show_bug.cgi?id=1219127
