# [H] CVE-2020-12654

## Summary
Severity: High
Advisory: CVE-2020-12654
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-12654
Type: osv

## Details
An issue was found in Linux kernel before 5.5.4. mwifiex_ret_wmm_get_status() in drivers/net/wireless/marvell/mwifiex/wmm.c allows a remote AP to trigger a heap-based buffer overflow because of an incorrect memcpy, aka CID-3a9b153c5591.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4392-1/
- https://usn.ubuntu.com/4393-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://www.debian.org/security/2020/dsa-4698
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.4
- https://security.netapp.com/advisory/ntap-20200608-0001/
- http://www.openwall.com/lists/oss-security/2020/05/08/2
- https://github.com/torvalds/linux/commit/3a9b153c5591548612c3955c9600a98150c81875
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3a9b153c5591548612c3955c9600a98150c81875
