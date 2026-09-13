# [C] RDMA/iwcm: Fix use-after-free of work objects after cm_id destruction

## Summary
Severity: Critical
Advisory: CVE-2025-38211
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38211
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/iwcm: Fix use-after-free of work objects after cm_id destruction

The commit 59c68ac31e15 ("iw_cm: free cm_id resources on the last
deref") simplified cm_id resource management by freeing cm_id once all
references to the cm_id were removed. The references are removed either
upon completion of iw_cm event handlers or when the application destroys
the cm_id. This commit introduced the use-after-free condition where
cm_id_private object could still be in use by event handler works during
the destruction of cm_id. The commit aee2424246f9 ("RDMA/iwcm: Fix a
use-after-free related to destroying CM IDs") addressed this use-after-
free by flushing all pending works at the cm_id destruction.

However, still another use-after-free possibility remained. It happens
with the work objects allocated for each cm_id_priv within
alloc_work_entries() during cm_id creation, and subsequently freed in
dealloc_work_entries() once all references to the cm_id are removed.
If the cm_id's last reference is decremented in the event handler work,
the work object for the work itself gets removed, and causes the use-
after-free BUG below:

  BUG: KASAN: slab-use-after-free in __pwq_activate_work+0x1ff/0x250
  Read of size 8 at addr ffff88811f9cf800 by task kworker/u16:1/147091

  CPU: 2 UID: 0 PID: 147091 Comm: kworker/u16:1 Not tainted 6.15.0-rc2+ #27 PREEMPT(voluntary)
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-3.fc41 04/01/2014
  Workqueue:  0x0 (iw_cm_wq)
  Call Trace:
   <TASK>
   dump_stack_lvl+0x6a/0x90
   print_report+0x174/0x554
   ? __virt_addr_valid+0x208/0x430
   ? __pwq_activate_work+0x1ff/0x250
   kasan_report+0xae/0x170
   ? __pwq_activate_work+0x1ff/0x250
   __pwq_activate_work+0x1ff/0x250
   pwq_dec_nr_in_flight+0x8c5/0xfb0
   process_one_work+0xc11/0x1460
   ? __pfx_process_one_work+0x10/0x10
   ? assign_work+0x16c/0x240
   worker_thread+0x5ef/0xfd0
   ? __pfx_worker_thread+0x10/0x10
   kthread+0x3b0/0x770
   ? __pfx_kthread+0x10/0x10
   ? rcu_is_watching+0x11/0xb0
   ? _raw_spin_unlock_irq+0x24/0x50
   ? rcu_is_watching+0x11/0xb0
   ? __pfx_kthread+0x10/0x10
   ret_from_fork+0x30/0x70
   ? __pfx_kthread+0x10/0x10
   ret_from_fork_asm+0x1a/0x30
   </TASK>

  Allocated by task 147416:
   kasan_save_stack+0x2c/0x50
   kasan_save_track+0x10/0x30
   __kasan_kmalloc+0xa6/0xb0
   alloc_work_entries+0xa9/0x260 [iw_cm]
   iw_cm_connect+0x23/0x4a0 [iw_cm]
   rdma_connect_locked+0xbfd/0x1920 [rdma_cm]
   nvme_rdma_cm_handler+0x8e5/0x1b60 [nvme_rdma]
   cma_cm_event_handler+0xae/0x320 [rdma_cm]
   cma_work_handler+0x106/0x1b0 [rdma_cm]
   process_one_work+0x84f/0x1460
   worker_thread+0x5ef/0xfd0
   kthread+0x3b0/0x770
   ret_from_fork+0x30/0x70
   ret_from_fork_asm+0x1a/0x30

  Freed by task 147091:
   kasan_save_stack+0x2c/0x50
   kasan_save_track+0x10/0x30
   kasan_save_free_info+0x37/0x60
   __kasan_slab_free+0x4b/0x70
   kfree+0x13a/0x4b0
   dealloc_work_entries+0x125/0x1f0 [iw_cm]
   iwcm_deref_id+0x6f/0xa0 [iw_cm]
   cm_work_handler+0x136/0x1ba0 [iw_cm]
   process_one_work+0x84f/0x1460
   worker_thread+0x5ef/0xfd0
   kthread+0x3b0/0x770
   ret_from_fork+0x30/0x70
   ret_from_fork_asm+0x1a/0x30

  Last potentially related work creation:
   kasan_save_stack+0x2c/0x50
   kasan_record_aux_stack+0xa3/0xb0
   __queue_work+0x2ff/0x1390
   queue_work_on+0x67/0xc0
   cm_event_handler+0x46a/0x820 [iw_cm]
   siw_cm_upcall+0x330/0x650 [siw]
   siw_cm_work_handler+0x6b9/0x2b20 [siw]
   process_one_work+0x84f/0x1460
   worker_thread+0x5ef/0xfd0
   kthread+0x3b0/0x770
   ret_from_fork+0x30/0x70
   ret_from_fork_asm+0x1a/0x30

This BUG is reproducible by repeating the blktests test case nvme/061
for the rdma transport and the siw driver.

To avoid the use-after-free of cm_id_private work objects, ensure that
the last reference to the cm_id is decremented not in the event handler
works, but in the cm_id destruction context. For that purpose, mo
---truncated---

## References
- https://git.kernel.org/stable/c/013dcdf6f03bcedbaf1669e3db71c34a197715b2
- https://git.kernel.org/stable/c/23a707bbcbea468eedb398832eeb7e8e0ceafd21
- https://git.kernel.org/stable/c/3b4a50d733acad6831f6bd9288a76a80f70650ac
- https://git.kernel.org/stable/c/6883b680e703c6b2efddb4e7a8d891ce1803d06b
- https://git.kernel.org/stable/c/764c9f69beabef8bdc651a7746c59f7a340d104f
- https://git.kernel.org/stable/c/78381dc8a6b61c9bb9987d37b4d671b99767c4a1
- https://git.kernel.org/stable/c/bf7eff5e3a36c54bbe8aff7fd6dd7c07490b81c5
- https://git.kernel.org/stable/c/fd960b5ddf4faf00da43babdd3acda68842e1f6a
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38211.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38211
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
