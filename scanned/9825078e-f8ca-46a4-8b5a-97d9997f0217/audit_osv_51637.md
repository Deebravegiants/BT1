# [M] CVE-2021-37159

## Summary
Severity: Medium
Advisory: CVE-2021-37159
Aliases: A-195082947, PUB-A-195082947
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2021-37159
Type: osv

## Details
hso_free_net_device in drivers/net/usb/hso.c in the Linux kernel through 5.13.4 calls unregister_netdev without checking for the NETREG_REGISTERED state, leading to a use-after-free and a double free.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a6ecfb39ba9d7316057cea823b196b734f6b18ca
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dcb713d53e2eadf42b878c12a471e74dc6ed3145
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://security.netapp.com/advisory/ntap-20210819-0003/
- https://bugzilla.suse.com/show_bug.cgi?id=1188601
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.spinics.net/lists/linux-usb/msg202228.html
