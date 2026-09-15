# [H] tracing/timerlat: Fix a race during cpuhp processing

## Summary
Severity: High
Advisory: CVE-2024-49866
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49866
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/timerlat: Fix a race during cpuhp processing

There is another found exception that the "timerlat/1" thread was
scheduled on CPU0, and lead to timer corruption finally:

```
ODEBUG: init active (active state 0) object: ffff888237c2e108 object type: hrtimer hint: timerlat_irq+0x0/0x220
WARNING: CPU: 0 PID: 426 at lib/debugobjects.c:518 debug_print_object+0x7d/0xb0
Modules linked in:
CPU: 0 UID: 0 PID: 426 Comm: timerlat/1 Not tainted 6.11.0-rc7+ #45
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1ubuntu1.1 04/01/2014
RIP: 0010:debug_print_object+0x7d/0xb0
...
Call Trace:
 <TASK>
 ? __warn+0x7c/0x110
 ? debug_print_object+0x7d/0xb0
 ? report_bug+0xf1/0x1d0
 ? prb_read_valid+0x17/0x20
 ? handle_bug+0x3f/0x70
 ? exc_invalid_op+0x13/0x60
 ? asm_exc_invalid_op+0x16/0x20
 ? debug_print_object+0x7d/0xb0
 ? debug_print_object+0x7d/0xb0
 ? __pfx_timerlat_irq+0x10/0x10
 __debug_object_init+0x110/0x150
 hrtimer_init+0x1d/0x60
 timerlat_main+0xab/0x2d0
 ? __pfx_timerlat_main+0x10/0x10
 kthread+0xb7/0xe0
 ? __pfx_kthread+0x10/0x10
 ret_from_fork+0x2d/0x40
 ? __pfx_kthread+0x10/0x10
 ret_from_fork_asm+0x1a/0x30
 </TASK>
```

After tracing the scheduling event, it was discovered that the migration
of the "timerlat/1" thread was performed during thread creation. Further
analysis confirmed that it is because the CPU online processing for
osnoise is implemented through workers, which is asynchronous with the
offline processing. When the worker was scheduled to create a thread, the
CPU may has already been removed from the cpu_online_mask during the offline
process, resulting in the inability to select the right CPU:

T1                       | T2
[CPUHP_ONLINE]           | cpu_device_down()
osnoise_hotplug_workfn() |
                         |     cpus_write_lock()
                         |     takedown_cpu(1)
                         |     cpus_write_unlock()
[CPUHP_OFFLINE]          |
    cpus_read_lock()     |
    start_kthread(1)     |
    cpus_read_unlock()   |

To fix this, skip online processing if the CPU is already offline.

## References
- https://git.kernel.org/stable/c/322920b53dc11f9c2b33397eb3ae5bc6a175b60d
- https://git.kernel.org/stable/c/829e0c9f0855f26b3ae830d17b24aec103f7e915
- https://git.kernel.org/stable/c/a0d9c0cd5856191e095cf43a2e141b73945b7716
- https://git.kernel.org/stable/c/a6e9849063a6c8f4cb2f652a437e44e3ed24356c
- https://git.kernel.org/stable/c/ce25f33ba89d6eefef64157655d318444580fa14
- https://git.kernel.org/stable/c/f72b451dc75578f644a3019c1489e9ae2c14e6c4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49866.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49866
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
