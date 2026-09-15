# [M] CVE-2022-24959

## Summary
Severity: Medium
Advisory: CVE-2022-24959
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-11
Source: https://osv.dev/vulnerability/CVE-2022-24959
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.16.5. There is a memory leak in yam_siocdevprivate in drivers/net/hamradio/yam.c.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.5
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5092
- https://www.debian.org/security/2022/dsa-5096
- https://github.com/torvalds/linux/commit/29eb31542787e1019208a2e1047bb7c76c069536
