# [H] CVE-2021-33034

## Summary
Severity: High
Advisory: CVE-2021-33034
Aliases: A-194694600, PUB-A-194694600
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-33034
Type: osv

## Details
In the Linux kernel before 5.12.4, net/bluetooth/hci_event.c has a use-after-free when destroying an hci_chan, aka CID-5c4c8c954409. This leads to writing an arbitrary value.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GI7Z7UBWBGD3ABNIL2DC7RQDCGA4UVQW/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5c4c8c9544099bb9043a10a5318130a943e32fc3
- https://sites.google.com/view/syzscope/kasan-use-after-free-read-in-hci_send_acl
- https://syzkaller.appspot.com/bug?id=2e1943a94647f7732dd6fc60368642d6e8dc91b1
