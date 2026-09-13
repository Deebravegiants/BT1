# [M] w1: fix WARNING after calling w1_process()

## Summary
Severity: Medium
Advisory: CVE-2022-49751
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49751
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <4.14.305, >=4.15.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

w1: fix WARNING after calling w1_process()

I got the following WARNING message while removing driver(ds2482):

------------[ cut here ]------------
do not call blocking ops when !TASK_RUNNING; state=1 set at [<000000002d50bfb6>] w1_process+0x9e/0x1d0 [wire]
WARNING: CPU: 0 PID: 262 at kernel/sched/core.c:9817 __might_sleep+0x98/0xa0
CPU: 0 PID: 262 Comm: w1_bus_master1 Tainted: G                 N 6.1.0-rc3+ #307
RIP: 0010:__might_sleep+0x98/0xa0
Call Trace:
 exit_signals+0x6c/0x550
 do_exit+0x2b4/0x17e0
 kthread_exit+0x52/0x60
 kthread+0x16d/0x1e0
 ret_from_fork+0x1f/0x30

The state of task is set to TASK_INTERRUPTIBLE in loop in w1_process(),
set it to TASK_RUNNING when it breaks out of the loop to avoid the
warning.

## References
- https://git.kernel.org/stable/c/190b5c3bbd5df685bb1063bda048831d72b8f1d4
- https://git.kernel.org/stable/c/216f35db6ec6a667cd9db4838d657c1d2f4684da
- https://git.kernel.org/stable/c/276052159ba94d4d9f5b453fb4707d6798c6b845
- https://git.kernel.org/stable/c/36225a7c72e9e3e1ce4001b6ce72849f5c9a2d3b
- https://git.kernel.org/stable/c/89c62cee5d4d65ac75d99b5f986f7f94290e888f
- https://git.kernel.org/stable/c/bccd6df4c177b1ad766f16565ccc298653d027d0
- https://git.kernel.org/stable/c/cfc7462ff824ed6718ed0272ee9aae88e20d469a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49751.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
