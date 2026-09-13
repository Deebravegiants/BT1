# [M] CVE-2017-12153

## Summary
Severity: Medium
Advisory: CVE-2017-12153
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-12153
Type: osv

## Details
A security flaw was discovered in the nl80211_set_rekey_data() function in net/wireless/nl80211.c in the Linux kernel through 4.13.3. This function does not check whether the required attributes are present in a Netlink request. This request can be issued by a user with the CAP_NET_ADMIN capability and may result in a NULL pointer dereference and system crash.

## References
- https://usn.ubuntu.com/3583-2/
- https://usn.ubuntu.com/3583-1/
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/100855
- http://seclists.org/oss-sec/2017/q3/437
- https://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211.git/commit/?id=e785fa0a164aa11001cba931367c7f94ffaff888
- https://bugzilla.novell.com/show_bug.cgi?id=1058410
- https://bugzilla.redhat.com/show_bug.cgi?id=1491046
- https://marc.info/?t=150525503100001&r=1&w=2
