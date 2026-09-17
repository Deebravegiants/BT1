# [H] CVE-2023-40283

## Summary
Severity: High
Advisory: CVE-2023-40283
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-14
Source: https://osv.dev/vulnerability/CVE-2023-40283
Type: osv

## Details
An issue was discovered in l2cap_sock_release in net/bluetooth/l2cap_sock.c in the Linux kernel before 6.4.10. There is a use-after-free because the children of an sk are mishandled.

## References
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.10
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20231020-0007/
- http://packetstormsecurity.com/files/175072/Kernel-Live-Patch-Security-Notice-LSN-0098-1.html
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1728137b33c00d5a2b5110ed7aafb42e7c32e4a1
- https://github.com/torvalds/linux/commit/1728137b33c00d5a2b5110ed7aafb42e7c32e4a1
