# [H] CVE-2019-11815

## Summary
Severity: High
Advisory: CVE-2019-11815
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-08
Source: https://osv.dev/vulnerability/CVE-2019-11815
Type: osv

## Details
An issue was discovered in rds_tcp_kill_sock in net/rds/tcp.c in the Linux kernel before 5.0.8. There is a race condition leading to a use-after-free, related to net namespace cleanup.

## References
- https://usn.ubuntu.com/4008-1/
- https://www.debian.org/security/2019/dsa-4465
- https://usn.ubuntu.com/4068-2/
- https://usn.ubuntu.com/4118-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.8
- https://security.netapp.com/advisory/ntap-20190719-0003/
- https://support.f5.com/csp/article/K32019083
- https://usn.ubuntu.com/4005-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00071.html
- http://www.securityfocus.com/bid/108283
- https://lists.debian.org/debian-lts-announce/2019/06/msg00011.html
- https://usn.ubuntu.com/4008-3/
- https://usn.ubuntu.com/4068-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00043.html
- http://packetstormsecurity.com/files/153799/Kernel-Live-Patch-Security-Notice-LSN-0053-1.html
- https://seclists.org/bugtraq/2019/Jun/26
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cb66ddd156203daefb8d71158036b27b0e2caf63
- https://github.com/torvalds/linux/commit/cb66ddd156203daefb8d71158036b27b0e2caf63
