# [H] CVE-2022-4744

## Summary
Severity: High
Advisory: CVE-2022-4744
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2022-4744
Type: osv

## Details
A double-free flaw was found in the Linux kernel’s TUN/TAP device driver functionality in how a user registers the device when the register_netdevice function fails (NETDEV_REGISTER notifier). This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- http://packetstormsecurity.com/files/171912/CentOS-Stream-9-Missing-Kernel-Security-Fix.html
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=158b515f703e
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://security.netapp.com/advisory/ntap-20230526-0009/
