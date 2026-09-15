# [M] CVE-2022-2663

## Summary
Severity: Medium
Advisory: CVE-2022-2663
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-2663
Type: osv

## Details
An issue was found in the Linux kernel in nf_conntrack_irc where the message handling can be confused and incorrectly matches the message. A firewall may be able to be bypassed when users are using unencrypted IRC with nf_conntrack_irc configured.

## References
- https://lore.kernel.org/netfilter-devel/20220826045658.100360-1-dgl%40dgl.cx/T/
- https://www.debian.org/security/2022/dsa-5257
- https://www.openwall.com/lists/oss-security/2022/08/30/1
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://www.youtube.com/watch?v=WIq-YgQuYCA
- https://dgl.cx/2022/08/nat-again-irc-cve-2022-2663
