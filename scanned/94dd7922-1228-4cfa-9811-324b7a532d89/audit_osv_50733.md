# [H] CVE-2020-36386

## Summary
Severity: High
Advisory: CVE-2020-36386
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2020-36386
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.8.1. net/bluetooth/hci_event.c has a slab out-of-bounds read in hci_extended_inquiry_result_evt, aka CID-51c19bf3d5cf.

## References
- https://sites.google.com/view/syzscope/kasan-slab-out-of-bounds-read-in-hci_extended_inquiry_result_evt
- https://syzkaller.appspot.com/bug?id=4bf11aa05c4ca51ce0df86e500fce486552dc8d2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=51c19bf3d5cfaa66571e4b88ba2a6f6295311101
- https://syzkaller.appspot.com/text?tag=ReproC&x=15ca2f46900000
