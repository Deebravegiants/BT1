# [M] CVE-2017-16911

## Summary
Severity: Medium
Advisory: CVE-2017-16911
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2017-16911
Type: osv

## Details
The vhci_hcd driver in the Linux Kernel before version 4.14.8 and 4.4.114 allows allows local attackers to disclose kernel memory addresses. Successful exploitation requires that a USB device is attached over IP.

## References
- https://usn.ubuntu.com/3619-2/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3754-1/
- https://secuniaresearch.flexerasoftware.com/advisories/80454/
- http://www.securityfocus.com/bid/102156
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-20/
- https://www.debian.org/security/2018/dsa-4187
- https://www.spinics.net/lists/linux-usb/msg163480.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.8
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/commit/drivers/usb/usbip?id=2f2d0088eb93db5c649d2a5e34a3800a8a935fc5
