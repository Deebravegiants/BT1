# [H] CVE-2020-12653

## Summary
Severity: High
Advisory: CVE-2020-12653
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-12653
Type: osv

## Details
An issue was found in Linux kernel before 5.5.4. The mwifiex_cmd_append_vsie_tlv() function in drivers/net/wireless/marvell/mwifiex/scan.c allows local users to gain privileges or cause a denial of service because of an incorrect memcpy and buffer overflow, aka CID-b70261a288ea.

## References
- http://www.openwall.com/lists/oss-security/2020/05/08/2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.4
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://www.debian.org/security/2020/dsa-4698
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b70261a288ea4d2f4ac7cd04be08a9f0f2de4f4d
- https://github.com/torvalds/linux/commit/b70261a288ea4d2f4ac7cd04be08a9f0f2de4f4d
