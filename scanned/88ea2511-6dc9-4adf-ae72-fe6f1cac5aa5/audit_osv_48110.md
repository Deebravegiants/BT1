# [H] CVE-2017-18222

## Summary
Severity: High
Advisory: CVE-2017-18222
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2017-18222
Type: osv

## Details
In the Linux kernel before 4.12, Hisilicon Network Subsystem (HNS) does not consider the ETH_SS_PRIV_FLAGS case when retrieving sset_count data, which allows local users to cause a denial of service (buffer overflow and memory corruption) or possibly have unspecified other impact, as demonstrated by incompatibility between hns_get_sset_count and ethtool_get_strings.

## References
- https://usn.ubuntu.com/3654-2/
- https://usn.ubuntu.com/3656-1/
- https://usn.ubuntu.com/3654-1/
- https://www.debian.org/security/2018/dsa-4188
- http://www.securityfocus.com/bid/103349
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=412b65d15a7f8a93794653968308fc100f2aa87c
- https://github.com/torvalds/linux/commit/412b65d15a7f8a93794653968308fc100f2aa87c
