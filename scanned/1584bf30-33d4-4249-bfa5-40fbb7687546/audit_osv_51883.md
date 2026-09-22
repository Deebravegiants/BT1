# [M] CVE-2021-43976

## Summary
Severity: Medium
Advisory: CVE-2021-43976
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-17
Source: https://osv.dev/vulnerability/CVE-2021-43976
Type: osv

## Details
In the Linux kernel through 5.15.2, mwifiex_usb_recv in drivers/net/wireless/marvell/mwifiex/usb.c allows an attacker (who can connect a crafted USB device) to cause a denial of service (skb_over_panic).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YODMYMGZYDXQKGJGX7TJG4XV4L5YLLBD/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=04d80663f67ccef893061b49ec8a42ff7045ae84
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X24M7KDC4OJOZNS3RDSYC7ELNELOLQ2N/
- https://patchwork.kernel.org/project/linux-wireless/patch/YX4CqjfRcTa6bVL+%40Zekuns-MBP-16.fios-router.home/
- https://www.debian.org/security/2022/dsa-5092
- https://www.debian.org/security/2022/dsa-5096
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20211210-0001/
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://www.oracle.com/security-alerts/cpujul2022.html
