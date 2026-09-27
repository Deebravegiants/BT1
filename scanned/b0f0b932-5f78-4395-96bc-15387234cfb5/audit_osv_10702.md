# [M] CVE-2017-18344

## Summary
Severity: Medium
Advisory: CVE-2017-18344
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-18344
Type: osv

## Details
The timer_create syscall implementation in kernel/time/posix-timers.c in the Linux kernel before 4.14.8 doesn't properly validate the sigevent->sigev_notify field, which leads to out-of-bounds access in the show_timer function (called when /proc/$PID/timers is read). This allows userspace applications to read arbitrary kernel memory (on a kernel built with CONFIG_POSIX_TIMERS and CONFIG_CHECKPOINT_RESTORE).

## References
- https://access.redhat.com/errata/RHSA-2018:3590
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.8
- https://usn.ubuntu.com/3742-1/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3459
- https://access.redhat.com/errata/RHSA-2018:3540
- https://access.redhat.com/errata/RHSA-2018:3586
- https://usn.ubuntu.com/3742-2/
- http://www.securitytracker.com/id/1041414
- https://access.redhat.com/errata/RHSA-2018:3591
- http://www.securityfocus.com/bid/104909
- https://access.redhat.com/errata/RHSA-2018:3096
- https://github.com/torvalds/linux/commit/cef31d9af908243421258f1df35a4a644604efbe
- https://www.exploit-db.com/exploits/45175/
