# [M] CVE-2020-36694

## Summary
Severity: Medium
Advisory: CVE-2020-36694
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-21
Source: https://osv.dev/vulnerability/CVE-2020-36694
Type: osv

## Details
An issue was discovered in netfilter in the Linux kernel before 5.10. There can be a use-after-free in the packet processing context, because the per-CPU sequence count is mishandled during concurrent iptables rules replacement. This could be exploited with the CAP_NET_ADMIN capability in an unprivileged namespace. NOTE: cc00bca was reverted in 5.12.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12
- https://security.netapp.com/advisory/ntap-20230622-0005/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cc00bcaa589914096edef7fb87ca5cee4a166b5c
- https://syzkaller.appspot.com/bug?id=0c4fd9c6aa04ec116d01e915d3b186f71a212cb2
