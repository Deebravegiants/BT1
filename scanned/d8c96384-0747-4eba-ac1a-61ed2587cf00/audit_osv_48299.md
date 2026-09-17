# [M] CVE-2017-5967

## Summary
Severity: Medium
Advisory: CVE-2017-5967
CVSS: 4.0 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-02-14
Source: https://osv.dev/vulnerability/CVE-2017-5967
Type: osv

## Details
The time subsystem in the Linux kernel through 4.9.9, when CONFIG_TIMER_STATS is enabled, allows local users to discover real PID values (as distinguished from PID values inside a PID namespace) by reading the /proc/timer_list file, related to the print_timer function in kernel/time/timer_list.c and the __timer_stats_timer_set_start_info function in kernel/time/timer.c.

## References
- http://www.securityfocus.com/bid/96271
- https://bugzilla.kernel.org/show_bug.cgi?id=193921
- http://git.kernel.org/cgit/linux/kernel/git/tip/tip.git/commit/?id=dfb4357da6ddbdf57d583ba64361c9d792b0e0b1
