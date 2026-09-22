# [H] drm/amdgpu: fix use-after-free during gpu recovery

## Summary
Severity: High
Advisory: CVE-2022-48990
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48990
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix use-after-free during gpu recovery

[Why]
    [  754.862560] refcount_t: underflow; use-after-free.
    [  754.862898] Call Trace:
    [  754.862903]  <TASK>
    [  754.862913]  amdgpu_job_free_cb+0xc2/0xe1 [amdgpu]
    [  754.863543]  drm_sched_main.cold+0x34/0x39 [amd_sched]

[How]
    The fw_fence may be not init, check whether dma_fence_init
    is performed before job free

## References
- https://git.kernel.org/stable/c/3cb93f390453cde4d6afda1587aaa00e75e09617
- https://git.kernel.org/stable/c/d2a89cd942edd50c1e652004fd64019be78b0a96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48990.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
