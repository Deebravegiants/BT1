# [H] iommu/vt-d: Fix suspicious RCU usage

## Summary
Severity: High
Advisory: CVE-2025-21876
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21876
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.18, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Fix suspicious RCU usage

Commit <d74169ceb0d2> ("iommu/vt-d: Allocate DMAR fault interrupts
locally") moved the call to enable_drhd_fault_handling() to a code
path that does not hold any lock while traversing the drhd list. Fix
it by ensuring the dmar_global_lock lock is held when traversing the
drhd list.

Without this fix, the following warning is triggered:
 =============================
 WARNING: suspicious RCU usage
 6.14.0-rc3 #55 Not tainted
 -----------------------------
 drivers/iommu/intel/dmar.c:2046 RCU-list traversed in non-reader section!!
               other info that might help us debug this:
               rcu_scheduler_active = 1, debug_locks = 1
 2 locks held by cpuhp/1/23:
 #0: ffffffff84a67c50 (cpu_hotplug_lock){++++}-{0:0}, at: cpuhp_thread_fun+0x87/0x2c0
 #1: ffffffff84a6a380 (cpuhp_state-up){+.+.}-{0:0}, at: cpuhp_thread_fun+0x87/0x2c0
 stack backtrace:
 CPU: 1 UID: 0 PID: 23 Comm: cpuhp/1 Not tainted 6.14.0-rc3 #55
 Call Trace:
  <TASK>
  dump_stack_lvl+0xb7/0xd0
  lockdep_rcu_suspicious+0x159/0x1f0
  ? __pfx_enable_drhd_fault_handling+0x10/0x10
  enable_drhd_fault_handling+0x151/0x180
  cpuhp_invoke_callback+0x1df/0x990
  cpuhp_thread_fun+0x1ea/0x2c0
  smpboot_thread_fn+0x1f5/0x2e0
  ? __pfx_smpboot_thread_fn+0x10/0x10
  kthread+0x12a/0x2d0
  ? __pfx_kthread+0x10/0x10
  ret_from_fork+0x4a/0x60
  ? __pfx_kthread+0x10/0x10
  ret_from_fork_asm+0x1a/0x30
  </TASK>

Holding the lock in enable_drhd_fault_handling() triggers a lockdep splat
about a possible deadlock between dmar_global_lock and cpu_hotplug_lock.
This is avoided by not holding dmar_global_lock when calling
iommu_device_register(), which initiates the device probe process.

## References
- https://git.kernel.org/stable/c/4117c72938493a77ab53cc4b8284be8fb6ec8065
- https://git.kernel.org/stable/c/b150654f74bf0df8e6a7936d5ec51400d9ec06d8
- https://git.kernel.org/stable/c/c603ccbe91d189849e1439134598ec567088dcec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21876.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21876
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
