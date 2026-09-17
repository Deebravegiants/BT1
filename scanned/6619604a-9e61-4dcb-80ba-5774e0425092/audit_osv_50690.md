# [M] CVE-2020-28915

## Summary
Severity: Medium
Advisory: CVE-2020-28915
CVSS: 5.8 (CVSS:3.1/AV:P/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H)
Published: 2020-11-18
Source: https://osv.dev/vulnerability/CVE-2020-28915
Type: osv

## Details
A buffer over-read (at the framebuffer layer) in the fbcon code in the Linux kernel before 5.8.15 could be used by local attackers to read kernel memory, aka CID-6735b4632def.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.15
- https://bugzilla.suse.com/show_bug.cgi?id=1178886
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5af08640795b2b9a940c9266c0260455377ae262
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6735b4632def0640dbdf4eb9f99816aca18c4f16
- https://syzkaller.appspot.com/bug?id=08b8be45afea11888776f897895aef9ad1c3ecfd
