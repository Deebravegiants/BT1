# [H] CVE-2016-9919

## Summary
Severity: High
Advisory: CVE-2016-9919
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-9919
Type: osv

## Details
The icmp6_send function in net/ipv6/icmp.c in the Linux kernel through 4.8.12 omits a certain check of the dst data structure, which allows remote attackers to cause a denial of service (panic) via a fragmented IPv6 packet.

## References
- http://www.openwall.com/lists/oss-security/2016/12/08/15
- http://www.securityfocus.com/bid/94824
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=79dc7e3f1cd323be4c81aa1a94faa1b3ed987fb2
- https://github.com/torvalds/linux/commit/79dc7e3f1cd323be4c81aa1a94faa1b3ed987fb2
