# [H] CVE-2019-25045

## Summary
Severity: High
Advisory: CVE-2019-25045
Aliases: A-191191823, PUB-A-191191823
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2019-25045
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.19. The XFRM subsystem has a use-after-free, related to an xfrm_state_fini panic, aka CID-dbb2483b2a46.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.19
- https://security.netapp.com/advisory/ntap-20210720-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=dbb2483b2a46fbaf833cfb5deb5ed9cace9c7399
- https://sites.google.com/view/syzscope/warning-in-xfrm_state_fini-2
- https://syzkaller.appspot.com/bug?id=f99edaeec58ad40380ed5813d89e205861be2896
