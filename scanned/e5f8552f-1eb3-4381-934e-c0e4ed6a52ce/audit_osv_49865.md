# [M] CVE-2019-20095

## Summary
Severity: Medium
Advisory: CVE-2019-20095
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-20095
Type: osv

## Details
mwifiex_tm_cmd in drivers/net/wireless/marvell/mwifiex/cfg80211.c in the Linux kernel before 5.1.6 has some error-handling cases that did not free allocated hostcmd memory, aka CID-003b686ace82. This will cause a memory leak and denial of service.

## References
- https://security.netapp.com/advisory/ntap-20200204-0002/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=003b686ace820ce2d635a83f10f2d7f9c147dabc
