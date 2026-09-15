# [H] drm/sched: Fix potential double free in drm_sched_job_add_resv_dependencies

## Summary
Severity: High
Advisory: CVE-2025-40096
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-40096
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sched: Fix potential double free in drm_sched_job_add_resv_dependencies

When adding dependencies with drm_sched_job_add_dependency(), that
function consumes the fence reference both on success and failure, so in
the latter case the dma_fence_put() on the error path (xarray failed to
expand) is a double free.

Interestingly this bug appears to have been present ever since
commit ebd5f74255b9 ("drm/sched: Add dependency tracking"), since the code
back then looked like this:

drm_sched_job_add_implicit_dependencies():
...
       for (i = 0; i < fence_count; i++) {
               ret = drm_sched_job_add_dependency(job, fences[i]);
               if (ret)
                       break;
       }

       for (; i < fence_count; i++)
               dma_fence_put(fences[i]);

Which means for the failing 'i' the dma_fence_put was already a double
free. Possibly there were no users at that time, or the test cases were
insufficient to hit it.

The bug was then only noticed and fixed after
commit 9c2ba265352a ("drm/scheduler: use new iterator in drm_sched_job_add_implicit_dependencies v2")
landed, with its fixup of
commit 4eaf02d6076c ("drm/scheduler: fix drm_sched_job_add_implicit_dependencies").

At that point it was a slightly different flavour of a double free, which
commit 963d0b356935 ("drm/scheduler: fix drm_sched_job_add_implicit_dependencies harder")
noticed and attempted to fix.

But it only moved the double free from happening inside the
drm_sched_job_add_dependency(), when releasing the reference not yet
obtained, to the caller, when releasing the reference already released by
the former in the failure case.

As such it is not easy to identify the right target for the fixes tag so
lets keep it simple and just continue the chain.

While fixing we also improve the comment and explain the reason for taking
the reference and not dropping it.

## References
- https://git.kernel.org/stable/c/4c38a63ae12ecc9370a7678077bde2d61aa80e9c
- https://git.kernel.org/stable/c/57239762aa90ad768dac055021f27705dae73344
- https://git.kernel.org/stable/c/5801e65206b065b0b2af032f7f1eef222aa2fd83
- https://git.kernel.org/stable/c/e5e3eb2aff92994ee81ce633f1c4e73bd4b87e11
- https://git.kernel.org/stable/c/fdfb47e85af1e11ec822c82739dde2dd8dff5115
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40096.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
