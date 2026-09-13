# [M] CVE-2015-9289

## Summary
Severity: Medium
Advisory: CVE-2015-9289
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-27
Source: https://osv.dev/vulnerability/CVE-2015-9289
Type: osv

## Details
In the Linux kernel before 4.1.4, a buffer overflow occurs when checking userspace params in drivers/media/dvb-frontends/cx24116.c. The maximum size for a DiSEqC command is 6, according to the userspace API. However, the code allows larger values such as 23.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1fa2337a315a2448c5434f41e00d56b01a22283c
- https://github.com/torvalds/linux/commit/1fa2337a315a2448c5434f41e00d56b01a22283c
- https://mirrors.edge.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.4
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1fa2337a315a2448c5434f41e00d56b01a22283c
- https://github.com/torvalds/linux/commit/1fa2337a315a2448c5434f41e00d56b01a22283c
