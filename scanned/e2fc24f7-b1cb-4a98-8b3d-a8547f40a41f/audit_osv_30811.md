# [H] media: i2c: tc358743: Fix crash in the probe error path when using polling

## Summary
Severity: High
Advisory: CVE-2024-56576
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56576
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: i2c: tc358743: Fix crash in the probe error path when using polling

If an error occurs in the probe() function, we should remove the polling
timer that was alarmed earlier, otherwise the timer is called with
arguments that are already freed, which results in a crash.

------------[ cut here ]------------
WARNING: CPU: 3 PID: 0 at kernel/time/timer.c:1830 __run_timers+0x244/0x268
Modules linked in:
CPU: 3 UID: 0 PID: 0 Comm: swapper/3 Not tainted 6.11.0 #226
Hardware name: Diasom DS-RK3568-SOM-EVB (DT)
pstate: 804000c9 (Nzcv daIF +PAN -UAO -TCO -DIT -SSBS BTYPE=--)
pc : __run_timers+0x244/0x268
lr : __run_timers+0x1d4/0x268
sp : ffffff80eff2baf0
x29: ffffff80eff2bb50 x28: 7fffffffffffffff x27: ffffff80eff2bb00
x26: ffffffc080f669c0 x25: ffffff80efef6bf0 x24: ffffff80eff2bb00
x23: 0000000000000000 x22: dead000000000122 x21: 0000000000000000
x20: ffffff80efef6b80 x19: ffffff80041c8bf8 x18: ffffffffffffffff
x17: ffffffc06f146000 x16: ffffff80eff27dc0 x15: 000000000000003e
x14: 0000000000000000 x13: 00000000000054da x12: 0000000000000000
x11: 00000000000639c0 x10: 000000000000000c x9 : 0000000000000009
x8 : ffffff80eff2cb40 x7 : ffffff80eff2cb40 x6 : ffffff8002bee480
x5 : ffffffc080cb2220 x4 : ffffffc080cb2150 x3 : 00000000000f4240
x2 : 0000000000000102 x1 : ffffff80eff2bb00 x0 : ffffff80041c8bf0
Call trace:
 __run_timers+0x244/0x268
 timer_expire_remote+0x50/0x68
 tmigr_handle_remote+0x388/0x39c
 run_timer_softirq+0x38/0x44
 handle_softirqs+0x138/0x298
 __do_softirq+0x14/0x20
 ____do_softirq+0x10/0x1c
 call_on_irq_stack+0x24/0x4c
 do_softirq_own_stack+0x1c/0x2c
 irq_exit_rcu+0x9c/0xcc
 el1_interrupt+0x48/0xc0
 el1h_64_irq_handler+0x18/0x24
 el1h_64_irq+0x7c/0x80
 default_idle_call+0x34/0x68
 do_idle+0x23c/0x294
 cpu_startup_entry+0x38/0x3c
 secondary_start_kernel+0x128/0x160
 __secondary_switched+0xb8/0xbc
---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/13193a97ddd5a6a5b11408ddbc1ae85588b1860c
- https://git.kernel.org/stable/c/1def915b1564f4375330bd113ea1d768a569cfd8
- https://git.kernel.org/stable/c/34a3466a92f50c51d984f0ec2e96864886d460eb
- https://git.kernel.org/stable/c/5c9ab34c87af718bdbf9faa2b1a6ba41d15380ea
- https://git.kernel.org/stable/c/815d14147068347e88c258233eb951b41b2792a6
- https://git.kernel.org/stable/c/869f38ae07f7df829da4951c3d1f7a2be09c2e9a
- https://git.kernel.org/stable/c/b59ab89bc83f7bff67f78c6caf484a84a6dd30f7
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56576.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
