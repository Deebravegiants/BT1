# [H] drm/amdgpu: fix a job->pasid access race in gpu recovery

## Summary
Severity: High
Advisory: CVE-2025-68793
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68793
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix a job->pasid access race in gpu recovery

Avoid a possible UAF in GPU recovery due to a race between
the sched timeout callback and the tdr work queue.

The gpu recovery function calls drm_sched_stop() and
later drm_sched_start().  drm_sched_start() restarts
the tdr queue which will eventually free the job.  If
the tdr queue frees the job before time out callback
completes, the job will be freed and we'll get a UAF
when accessing the pasid.  Cache it early to avoid the
UAF.

Example KASAN trace:
[  493.058141] BUG: KASAN: slab-use-after-free in amdgpu_device_gpu_recover+0x968/0x990 [amdgpu]
[  493.067530] Read of size 4 at addr ffff88b0ce3f794c by task kworker/u128:1/323
[  493.074892]
[  493.076485] CPU: 9 UID: 0 PID: 323 Comm: kworker/u128:1 Tainted: G            E       6.16.0-1289896.2.zuul.bf4f11df81c1410bbe901c4373305a31 #1 PREEMPT(voluntary)
[  493.076493] Tainted: [E]=UNSIGNED_MODULE
[  493.076495] Hardware name: TYAN B8021G88V2HR-2T/S8021GM2NR-2T, BIOS V1.03.B10 04/01/2019
[  493.076500] Workqueue: amdgpu-reset-dev drm_sched_job_timedout [gpu_sched]
[  493.076512] Call Trace:
[  493.076515]  <TASK>
[  493.076518]  dump_stack_lvl+0x64/0x80
[  493.076529]  print_report+0xce/0x630
[  493.076536]  ? _raw_spin_lock_irqsave+0x86/0xd0
[  493.076541]  ? __pfx__raw_spin_lock_irqsave+0x10/0x10
[  493.076545]  ? amdgpu_device_gpu_recover+0x968/0x990 [amdgpu]
[  493.077253]  kasan_report+0xb8/0xf0
[  493.077258]  ? amdgpu_device_gpu_recover+0x968/0x990 [amdgpu]
[  493.077965]  amdgpu_device_gpu_recover+0x968/0x990 [amdgpu]
[  493.078672]  ? __pfx_amdgpu_device_gpu_recover+0x10/0x10 [amdgpu]
[  493.079378]  ? amdgpu_coredump+0x1fd/0x4c0 [amdgpu]
[  493.080111]  amdgpu_job_timedout+0x642/0x1400 [amdgpu]
[  493.080903]  ? pick_task_fair+0x24e/0x330
[  493.080910]  ? __pfx_amdgpu_job_timedout+0x10/0x10 [amdgpu]
[  493.081702]  ? _raw_spin_lock+0x75/0xc0
[  493.081708]  ? __pfx__raw_spin_lock+0x10/0x10
[  493.081712]  drm_sched_job_timedout+0x1b0/0x4b0 [gpu_sched]
[  493.081721]  ? __pfx__raw_spin_lock_irq+0x10/0x10
[  493.081725]  process_one_work+0x679/0xff0
[  493.081732]  worker_thread+0x6ce/0xfd0
[  493.081736]  ? __pfx_worker_thread+0x10/0x10
[  493.081739]  kthread+0x376/0x730
[  493.081744]  ? __pfx_kthread+0x10/0x10
[  493.081748]  ? __pfx__raw_spin_lock_irq+0x10/0x10
[  493.081751]  ? __pfx_kthread+0x10/0x10
[  493.081755]  ret_from_fork+0x247/0x330
[  493.081761]  ? __pfx_kthread+0x10/0x10
[  493.081764]  ret_from_fork_asm+0x1a/0x30
[  493.081771]  </TASK>

(cherry picked from commit 20880a3fd5dd7bca1a079534cf6596bda92e107d)

## References
- https://git.kernel.org/stable/c/77f73253015cbc7893fca1821ac3eae9eb4bc943
- https://git.kernel.org/stable/c/dac58c012c47cadf337a35eb05d44498c43e5cd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68793.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68793
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
