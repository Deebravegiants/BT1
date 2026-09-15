# [H] CVE-2022-41222

## Summary
Severity: High
Advisory: CVE-2022-41222
Aliases: A-248354871, ASB-A-248354871
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-41222
Type: osv

## Details
mm/mremap.c in the Linux kernel before 5.13.3 has a use-after-free via a stale TLB because an rmap lock is not held during a PUD move.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://security.netapp.com/advisory/ntap-20230214-0008/
- http://packetstormsecurity.com/files/168466/Linux-Stable-5.4-5.10-Use-After-Free-Race-Condition.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.3
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=97113eb39fa7972722ff490b947d8af023e1f6a2
- http://packetstormsecurity.com/files/171005/Kernel-Live-Patch-Security-Notice-LNS-0091-1.html
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2347
