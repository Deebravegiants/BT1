# [H] posix-cpu-timers: Cleanup CPU timers before freeing them during exec

## Summary
Severity: High
Advisory: CVE-2022-50095
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50095
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

posix-cpu-timers: Cleanup CPU timers before freeing them during exec

Commit 55e8c8eb2c7b ("posix-cpu-timers: Store a reference to a pid not a
task") started looking up tasks by PID when deleting a CPU timer.

When a non-leader thread calls execve, it will switch PIDs with the leader
process. Then, as it calls exit_itimers, posix_cpu_timer_del cannot find
the task because the timer still points out to the old PID.

That means that armed timers won't be disarmed, that is, they won't be
removed from the timerqueue_list. exit_itimers will still release their
memory, and when that list is later processed, it leads to a
use-after-free.

Clean up the timers from the de-threaded task before freeing them. This
prevents a reported use-after-free.

## References
- https://git.kernel.org/stable/c/541840859ace9c2ccebc32fa9e376c7bd3def490
- https://git.kernel.org/stable/c/9e255ed238fc67058df87b0388ad6d4b2ef3a2bd
- https://git.kernel.org/stable/c/b2fc1723eb65abb83e00d5f011de670296af0b28
- https://git.kernel.org/stable/c/e362359ace6f87c201531872486ff295df306d13
- https://git.kernel.org/stable/c/e8cb6e8fd9890780f1bfcf5592889e1b879e779c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50095.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
