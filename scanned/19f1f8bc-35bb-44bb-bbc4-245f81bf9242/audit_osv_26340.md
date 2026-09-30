# [M] Input: cyapa - add missing input core locking to suspend/resume functions

## Summary
Severity: Medium
Advisory: CVE-2023-52884
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2023-52884
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: cyapa - add missing input core locking to suspend/resume functions

Grab input->mutex during suspend/resume functions like it is done in
other input drivers. This fixes the following warning during system
suspend/resume cycle on Samsung Exynos5250-based Snow Chromebook:

------------[ cut here ]------------
WARNING: CPU: 1 PID: 1680 at drivers/input/input.c:2291 input_device_enabled+0x68/0x6c
Modules linked in: ...
CPU: 1 PID: 1680 Comm: kworker/u4:12 Tainted: G        W          6.6.0-rc5-next-20231009 #14109
Hardware name: Samsung Exynos (Flattened Device Tree)
Workqueue: events_unbound async_run_entry_fn
 unwind_backtrace from show_stack+0x10/0x14
 show_stack from dump_stack_lvl+0x58/0x70
 dump_stack_lvl from __warn+0x1a8/0x1cc
 __warn from warn_slowpath_fmt+0x18c/0x1b4
 warn_slowpath_fmt from input_device_enabled+0x68/0x6c
 input_device_enabled from cyapa_gen3_set_power_mode+0x13c/0x1dc
 cyapa_gen3_set_power_mode from cyapa_reinitialize+0x10c/0x15c
 cyapa_reinitialize from cyapa_resume+0x48/0x98
 cyapa_resume from dpm_run_callback+0x90/0x298
 dpm_run_callback from device_resume+0xb4/0x258
 device_resume from async_resume+0x20/0x64
 async_resume from async_run_entry_fn+0x40/0x15c
 async_run_entry_fn from process_scheduled_works+0xbc/0x6a8
 process_scheduled_works from worker_thread+0x188/0x454
 worker_thread from kthread+0x108/0x140
 kthread from ret_from_fork+0x14/0x28
Exception stack(0xf1625fb0 to 0xf1625ff8)
...
---[ end trace 0000000000000000 ]---
...
------------[ cut here ]------------
WARNING: CPU: 1 PID: 1680 at drivers/input/input.c:2291 input_device_enabled+0x68/0x6c
Modules linked in: ...
CPU: 1 PID: 1680 Comm: kworker/u4:12 Tainted: G        W          6.6.0-rc5-next-20231009 #14109
Hardware name: Samsung Exynos (Flattened Device Tree)
Workqueue: events_unbound async_run_entry_fn
 unwind_backtrace from show_stack+0x10/0x14
 show_stack from dump_stack_lvl+0x58/0x70
 dump_stack_lvl from __warn+0x1a8/0x1cc
 __warn from warn_slowpath_fmt+0x18c/0x1b4
 warn_slowpath_fmt from input_device_enabled+0x68/0x6c
 input_device_enabled from cyapa_gen3_set_power_mode+0x13c/0x1dc
 cyapa_gen3_set_power_mode from cyapa_reinitialize+0x10c/0x15c
 cyapa_reinitialize from cyapa_resume+0x48/0x98
 cyapa_resume from dpm_run_callback+0x90/0x298
 dpm_run_callback from device_resume+0xb4/0x258
 device_resume from async_resume+0x20/0x64
 async_resume from async_run_entry_fn+0x40/0x15c
 async_run_entry_fn from process_scheduled_works+0xbc/0x6a8
 process_scheduled_works from worker_thread+0x188/0x454
 worker_thread from kthread+0x108/0x140
 kthread from ret_from_fork+0x14/0x28
Exception stack(0xf1625fb0 to 0xf1625ff8)
...
---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/7b4e0b39182cf5e677c1fc092a3ec40e621c25b6
- https://git.kernel.org/stable/c/9400caf566f65c703e99d95f87b00c4b445627a7
- https://git.kernel.org/stable/c/a4c638ab25786bd5aab5978fe51b2b9be16a4ebd
- https://git.kernel.org/stable/c/a5fc298fa8f67cf1f0e1fc126eab70578cd40adc
- https://git.kernel.org/stable/c/f99809fdeb50d65bcbc1661ef391af94eebb8a75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52884.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52884
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
