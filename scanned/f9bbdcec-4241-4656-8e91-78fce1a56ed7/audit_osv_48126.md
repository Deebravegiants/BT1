# [M] CVE-2017-18261

## Summary
Severity: Medium
Advisory: CVE-2017-18261
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-19
Source: https://osv.dev/vulnerability/CVE-2017-18261
Type: osv

## Details
The arch_timer_reg_read_stable macro in arch/arm64/include/asm/arch_timer.h in the Linux kernel before 4.13 allows local users to cause a denial of service (infinite recursion) by writing to a file under /sys/kernel/debug in certain circumstances, as demonstrated by a scenario involving debugfs, ftrace, PREEMPT_TRACER, and FUNCTION_GRAPH_TRACER.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=adb4f11e0a8f4e29900adb2b7af28b6bbd5c1fa4
- https://github.com/torvalds/linux/commit/adb4f11e0a8f4e29900adb2b7af28b6bbd5c1fa4
