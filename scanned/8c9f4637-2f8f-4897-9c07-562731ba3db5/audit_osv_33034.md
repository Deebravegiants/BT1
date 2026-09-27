# [H] iommu/vt-d: Fix UAF on sva unbind with pending IOPFs

## Summary
Severity: High
Advisory: CVE-2025-38594
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38594
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Fix UAF on sva unbind with pending IOPFs

Commit 17fce9d2336d ("iommu/vt-d: Put iopf enablement in domain attach
path") disables IOPF on device by removing the device from its IOMMU's
IOPF queue when the last IOPF-capable domain is detached from the device.
Unfortunately, it did this in a wrong place where there are still pending
IOPFs. As a result, a use-after-free error is potentially triggered and
eventually a kernel panic with a kernel trace similar to the following:

 refcount_t: underflow; use-after-free.
 WARNING: CPU: 3 PID: 313 at lib/refcount.c:28 refcount_warn_saturate+0xd8/0xe0
 Workqueue: iopf_queue/dmar0-iopfq iommu_sva_handle_iopf
 Call Trace:
   <TASK>
   iopf_free_group+0xe/0x20
   process_one_work+0x197/0x3d0
   worker_thread+0x23a/0x350
   ? rescuer_thread+0x4a0/0x4a0
   kthread+0xf8/0x230
   ? finish_task_switch.isra.0+0x81/0x260
   ? kthreads_online_cpu+0x110/0x110
   ? kthreads_online_cpu+0x110/0x110
   ret_from_fork+0x13b/0x170
   ? kthreads_online_cpu+0x110/0x110
   ret_from_fork_asm+0x11/0x20
   </TASK>
  ---[ end trace 0000000000000000 ]---

The intel_pasid_tear_down_entry() function is responsible for blocking
hardware from generating new page faults and flushing all in-flight
ones. Therefore, moving iopf_for_domain_remove() after this function
should resolve this.

## References
- https://git.kernel.org/stable/c/c68332b7ee893292bba6e87d31ef2080c066c65d
- https://git.kernel.org/stable/c/f0b9d31c6edd50a6207489cd1bd4ddac814b9cd2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38594.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38594
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
