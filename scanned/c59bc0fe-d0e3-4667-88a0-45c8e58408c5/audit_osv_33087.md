# [H] drm/xe: Fix vm_bind_ioctl double free bug

## Summary
Severity: High
Advisory: CVE-2025-38731
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-38731
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Fix vm_bind_ioctl double free bug

If the argument check during an array bind fails, the bind_ops are freed
twice as seen below. Fix this by setting bind_ops to NULL after freeing.

==================================================================
BUG: KASAN: double-free in xe_vm_bind_ioctl+0x1b2/0x21f0 [xe]
Free of addr ffff88813bb9b800 by task xe_vm/14198

CPU: 5 UID: 0 PID: 14198 Comm: xe_vm Not tainted 6.16.0-xe-eudebug-cmanszew+ #520 PREEMPT(full)
Hardware name: Intel Corporation Alder Lake Client Platform/AlderLake-P DDR5 RVP, BIOS ADLPFWI1.R00.2411.A02.2110081023 10/08/2021
Call Trace:
 <TASK>
 dump_stack_lvl+0x82/0xd0
 print_report+0xcb/0x610
 ? __virt_addr_valid+0x19a/0x300
 ? xe_vm_bind_ioctl+0x1b2/0x21f0 [xe]
 kasan_report_invalid_free+0xc8/0xf0
 ? xe_vm_bind_ioctl+0x1b2/0x21f0 [xe]
 ? xe_vm_bind_ioctl+0x1b2/0x21f0 [xe]
 check_slab_allocation+0x102/0x130
 kfree+0x10d/0x440
 ? should_fail_ex+0x57/0x2f0
 ? xe_vm_bind_ioctl+0x1b2/0x21f0 [xe]
 xe_vm_bind_ioctl+0x1b2/0x21f0 [xe]
 ? __pfx_xe_vm_bind_ioctl+0x10/0x10 [xe]
 ? __lock_acquire+0xab9/0x27f0
 ? lock_acquire+0x165/0x300
 ? drm_dev_enter+0x53/0xe0 [drm]
 ? find_held_lock+0x2b/0x80
 ? drm_dev_exit+0x30/0x50 [drm]
 ? drm_ioctl_kernel+0x128/0x1c0 [drm]
 drm_ioctl_kernel+0x128/0x1c0 [drm]
 ? __pfx_xe_vm_bind_ioctl+0x10/0x10 [xe]
 ? find_held_lock+0x2b/0x80
 ? __pfx_drm_ioctl_kernel+0x10/0x10 [drm]
 ? should_fail_ex+0x57/0x2f0
 ? __pfx_xe_vm_bind_ioctl+0x10/0x10 [xe]
 drm_ioctl+0x352/0x620 [drm]
 ? __pfx_drm_ioctl+0x10/0x10 [drm]
 ? __pfx_rpm_resume+0x10/0x10
 ? do_raw_spin_lock+0x11a/0x1b0
 ? find_held_lock+0x2b/0x80
 ? __pm_runtime_resume+0x61/0xc0
 ? rcu_is_watching+0x20/0x50
 ? trace_irq_enable.constprop.0+0xac/0xe0
 xe_drm_ioctl+0x91/0xc0 [xe]
 __x64_sys_ioctl+0xb2/0x100
 ? rcu_is_watching+0x20/0x50
 do_syscall_64+0x68/0x2e0
 entry_SYSCALL_64_after_hwframe+0x76/0x7e
RIP: 0033:0x7fa9acb24ded

(cherry picked from commit a01b704527c28a2fd43a17a85f8996b75ec8492a)

## References
- https://git.kernel.org/stable/c/111fb43a557726079a67ce3ab51f602ddbf7097e
- https://git.kernel.org/stable/c/77a946bf1af0e8110ef6e243394217a17f9b7e33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38731.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
