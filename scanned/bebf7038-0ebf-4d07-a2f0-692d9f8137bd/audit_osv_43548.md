# [H] drm/amdgpu: fix KASAN slab-out-of-bounds in amdgpu_coredump ring dump

## Summary
Severity: High
Advisory: CVE-2026-74357
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74357
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix KASAN slab-out-of-bounds in amdgpu_coredump ring dump

The ring content dump in amdgpu_coredump() uses two separate loops over
adev->rings[]: the first counts rings with unsignalled fences to size
the allocation, and the second copies ring data into the allocated
buffers.

Both loops use the same condition to skip rings:

    atomic_read(&ring->fence_drv.last_seq) == ring->fence_drv.sync_seq

Because last_seq is an atomic that is updated concurrently by the fence
signalling path, additional rings may appear unsignalled in the second
loop that were signalled during the first. When this happens, idx
exceeds the allocated ring_count and the store to coredump->rings[idx]
writes past the end of the kcalloc-ed buffer.

This was found during IGT stressful test amd_queue_reset which
triggers random GPU resets. The OVERSIZE subtest
(CMD_STREAM_EXEC_INVALID_PACKET_LENGTH_OVERSIZE on GFX ring) provokes
a ring timeout and subsequent coredump, which hits the race between
the counting and copying loops. The failure is non-deterministic and
depends on fence signalling timing during the reset.

KASAN log:

  BUG: KASAN: slab-out-of-bounds in amdgpu_coredump+0x1274/0x12f0 [amdgpu]
  Write of size 4 at addr ffff888106154258 by task kworker/u128:5/23625
  CPU: 16 UID: 0 PID: 23625 Comm: kworker/u128:5 Not tainted 6.19.0+ #35
  Workqueue: amdgpu-reset-dev drm_sched_job_timedout [gpu_sched]
  Call Trace:
   <TASK>
   dump_stack_lvl+0xa5/0x110
   print_report+0xd1/0x660
   kasan_report+0xf3/0x130
   __asan_report_store4_noabort+0x17/0x30
   amdgpu_coredump+0x1274/0x12f0 [amdgpu]
   amdgpu_job_timedout+0xef0/0x16c0 [amdgpu]
   drm_sched_job_timedout+0x194/0x5c0 [gpu_sched]
   process_one_work+0x84b/0x1990
   worker_thread+0x6b8/0x11b0
   </TASK>

  Allocated by task 23625:
   kasan_save_stack+0x39/0x70
   __kasan_kmalloc+0xc3/0xd0
   __kmalloc_noprof+0x2ec/0x910
   amdgpu_coredump+0x5c5/0x12f0 [amdgpu]
   amdgpu_job_timedout+0xef0/0x16c0 [amdgpu]

  The buggy address belongs to the object at ffff888106154200
   which belongs to the cache kmalloc-rnd-09-96 of size 96
  The buggy address is located 16 bytes to the right of
   allocated 72-byte region [ffff888106154200, ffff888106154248)

72 bytes = 3 * sizeof(struct amdgpu_coredump_ring), so ring_count was 3
but idx reached 3+, writing ring_index (at struct offset 16) 16 bytes
past the allocation.

Fix by adding an idx < ring_count guard to the copy loop so it cannot
exceed the allocated count even when the fence state changes between
the two passes.

## References
- https://git.kernel.org/stable/c/08ac3a7879d300302a1927ce2038629539a37f8b
- https://git.kernel.org/stable/c/efb1dadaeb897b22b9e118d398d0f41e70e9ccca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74357.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74357
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
