# [H] CVE-2023-51781

## Summary
Severity: High
Advisory: CVE-2023-51781
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-11
Source: https://osv.dev/vulnerability/CVE-2023-51781
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.6.8. atalk_ioctl in net/appletalk/ddp.c has a use-after-free because of an atalk_recvmsg race condition.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.8
- https://github.com/torvalds/linux/commit/189ff16722ee36ced4d2a2469d4ab65a8fee4198
