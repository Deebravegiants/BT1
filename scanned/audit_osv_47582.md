# [M] CVE-2016-8658

## Summary
Severity: Medium
Advisory: CVE-2016-8658
CVSS: 6.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-8658
Type: osv

## Details
Stack-based buffer overflow in the brcmf_cfg80211_start_ap function in drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c in the Linux kernel before 4.7.5 allows local users to cause a denial of service (system crash) or possibly have unspecified other impact via a long SSID Information Element in a command to a Netlink socket.

## References
- http://www.securityfocus.com/bid/93541
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.5
- http://www.ubuntu.com/usn/USN-3145-1
- http://www.ubuntu.com/usn/USN-3146-1
- http://www.ubuntu.com/usn/USN-3146-2
- http://www.ubuntu.com/usn/USN-3145-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1384403
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ded89912156b1a47d940a0c954c43afbabd0c42c
- https://github.com/torvalds/linux/commit/ded89912156b1a47d940a0c954c43afbabd0c42c
- http://www.openwall.com/lists/oss-security/2016/10/13/1
