# [M] drm/sched: Check scheduler work queue before calling timeout handling

## Summary
Severity: Medium
Advisory: CVE-2023-53351
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53351
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sched: Check scheduler work queue before calling timeout handling

During an IGT GPU reset test we see again oops despite of
commit 0c8c901aaaebc9 (drm/sched: Check scheduler ready before calling
timeout handling).

It uses ready condition whether to call drm_sched_fault which unwind
the TDR leads to GPU reset.
However it looks the ready condition is overloaded with other meanings,
for example, for the following stack is related GPU reset :

0  gfx_v9_0_cp_gfx_start
1  gfx_v9_0_cp_gfx_resume
2  gfx_v9_0_cp_resume
3  gfx_v9_0_hw_init
4  gfx_v9_0_resume
5  amdgpu_device_ip_resume_phase2

does the following:
	/* start the ring */
	gfx_v9_0_cp_gfx_start(adev);
	ring->sched.ready = true;

The same approach is for other ASICs as well :
gfx_v8_0_cp_gfx_resume
gfx_v10_0_kiq_resume, etc...

As a result, our GPU reset test causes GPU fault which calls unconditionally gfx_v9_0_fault
and then drm_sched_fault. However now it depends on whether the interrupt service routine
drm_sched_fault is executed after gfx_v9_0_cp_gfx_start is completed which sets the ready
field of the scheduler to true even  for uninitialized schedulers and causes oops vs
no fault or when ISR  drm_sched_fault is completed prior  gfx_v9_0_cp_gfx_start and
NULL pointer dereference does not occur.

Use the field timeout_wq  to prevent oops for uninitialized schedulers.
The field could be initialized by the work queue of resetting the domain.

v1: Corrections to commit message (Luben)

## References
- https://git.kernel.org/stable/c/2da5bffe9eaa5819a868e8eaaa11b3fd0f16a691
- https://git.kernel.org/stable/c/c43a96fc00b662cef1ef0eb22d40441ce2abae8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53351.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53351
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
