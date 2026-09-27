# [H] drm/v3d: Fix use-after-free of CPU job query arrays on error path

## Summary
Severity: High
Advisory: CVE-2026-64099
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64099
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.93, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/v3d: Fix use-after-free of CPU job query arrays on error path

The CPU job ioctl's fail label calls kvfree() on cpu_job's timestamp and
performance query arrays after v3d_job_cleanup(), which drops the job's
last reference and frees cpu_job. Reading cpu_job at that point is a
use-after-free. Also, on the early v3d_job_init() failure path, it is a
NULL dereference, since v3d_job_deallocate() zeroes the local pointer.

In the success path, the arrays are released from the scheduler's
.free_job callback, but on the error path, they are freed manually, as
the job was never pushed to the scheduler. While the success path deals
with this correctly, the fail path doesn't.

On top of that, the manual kvfree() calls only free the array storage;
they don't drm_syncobj_put() the per-query syncobjs that
v3d_timestamp_query_info_free() and v3d_performance_query_info_free()
release on the success path. So the same fail path that triggers the
use-after-free also leaks one syncobj reference per query.

Unify the CPU job teardown into the CPU job's kref destructor, mirroring
v3d_render_job_free(). The scheduler's .free_job slot reverts to the
generic v3d_sched_job_free() and the fail label drops the manual
kvfree() calls, leaving a single teardown path that is reached from both
the scheduler and the ioctl error path. That removes the use-after-free,
the NULL dereference, and the syncobj leak by construction.

## References
- https://git.kernel.org/stable/c/0f8efc45740b0628a787d1b0be8a0ddabd700625
- https://git.kernel.org/stable/c/69c2a1fec2e7ca25598180816f3bc56e1842eb41
- https://git.kernel.org/stable/c/acd55ea40d03e06f20a9986363019e0e5173990e
- https://git.kernel.org/stable/c/b0fe80c0b9250b35e2211bf3117e7aca814a21b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
