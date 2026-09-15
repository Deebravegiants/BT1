# [H] CVE-2017-7541

## Summary
Severity: High
Advisory: CVE-2017-7541
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-7541
Type: osv

## Details
The brcmf_cfg80211_mgmt_tx function in drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c in the Linux kernel before 4.12.3 allows local users to cause a denial of service (buffer overflow and system crash) or possibly gain privileges via a crafted NL80211_CMD_FRAME Netlink packet.

## References
- http://www.debian.org/security/2017/dsa-3927
- https://access.redhat.com/errata/RHSA-2017:2930
- https://access.redhat.com/errata/RHSA-2017:2931
- http://www.debian.org/security/2017/dsa-3945
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.3
- http://www.securitytracker.com/id/1038981
- http://www.securityfocus.com/bid/99955
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:2863
- https://source.android.com/security/bulletin/2017-11-01
- https://github.com/torvalds/linux/commit/8f44c9a41386729fea410e688959ddaa9d51be7c
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8f44c9a41386729fea410e688959ddaa9d51be7c
- https://www.spinics.net/lists/stable/msg180994.html
- http://openwall.com/lists/oss-security/2017/07/24/2
- https://bugzilla.novell.com/show_bug.cgi?id=1049645
- https://bugzilla.redhat.com/show_bug.cgi?id=1473198
