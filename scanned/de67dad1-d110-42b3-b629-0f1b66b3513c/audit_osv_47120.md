# [M] CVE-2015-8964

## Summary
Severity: Medium
Advisory: CVE-2015-8964
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2015-8964
Type: osv

## Details
The tty_set_termios_ldisc function in drivers/tty/tty_ldisc.c in the Linux kernel before 4.5 allows local users to obtain sensitive information from kernel memory by reading a tty data structure.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dd42bf1197144ede075a9d4793123f7689e164bc
- http://source.android.com/security/bulletin/2016-11-01.html
- https://github.com/torvalds/linux/commit/dd42bf1197144ede075a9d4793123f7689e164bc
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dd42bf1197144ede075a9d4793123f7689e164bc
- https://github.com/torvalds/linux/commit/dd42bf1197144ede075a9d4793123f7689e164bc
- http://www.securityfocus.com/bid/94138
