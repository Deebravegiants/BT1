# [M] CVE-2017-16913

## Summary
Severity: Medium
Advisory: CVE-2017-16913
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2017-16913
Type: osv

## Details
The "stub_recv_cmd_submit()" function (drivers/usb/usbip/stub_rx.c) in the Linux Kernel before version 4.14.8, 4.9.71, and 4.4.114 when handling CMD_SUBMIT packets allows attackers to cause a denial of service (arbitrary memory allocation) via a specially crafted USB over IP packet.

## References
- https://usn.ubuntu.com/3619-2/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/102150
- https://secuniaresearch.flexerasoftware.com/advisories/80601/
- https://www.debian.org/security/2018/dsa-4187
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-21/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.114
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.71
- https://www.spinics.net/lists/linux-usb/msg163480.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.8
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/commit/drivers/usb/usbip?id=c6688ef9f29762e65bce325ef4acd6c675806366
