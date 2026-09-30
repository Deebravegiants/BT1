# [H] CVE-2018-25015

## Summary
Severity: High
Advisory: CVE-2018-25015
Aliases: A-191191879, PUB-A-191191879
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2018-25015
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.14.16. There is a use-after-free in net/sctp/socket.c for a held lock after a peel off, aka CID-a0ff660058b8.

## References
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.16
- https://security.netapp.com/advisory/ntap-20210720-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a0ff660058b88d12625a783ce9e5c1371c87951f
- https://sites.google.com/view/syzscope/warning-held-lock-freed
- https://syzkaller.appspot.com/bug?id=a8d38d1b68ffc744c53bd9b9fc1dbd6c86b1afe2
