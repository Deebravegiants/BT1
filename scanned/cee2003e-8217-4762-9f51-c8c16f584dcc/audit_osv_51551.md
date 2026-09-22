# [H] CVE-2021-33033

## Summary
Severity: High
Advisory: CVE-2021-33033
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-33033
Type: osv

## Details
The Linux kernel before 5.11.14 has a use-after-free in cipso_v4_genopt in net/ipv4/cipso_ipv4.c because the CIPSO and CALIPSO refcounting for the DOI definitions is mishandled, aka CID-ad5d07f4a9cd. This leads to writing an arbitrary value.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.14
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1165affd484889d4986cf3b724318935a0b120d8
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ad5d07f4a9cd671233ae20983848874731102c08
- https://sites.google.com/view/syzscope/kasan-use-after-free-read-in-cipso_v4_genopt
- https://syzkaller.appspot.com/bug?id=96e7d345748d8814901c91cd92084ed04b46701e
