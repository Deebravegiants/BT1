# [H] drm/amdkfd: Fix kfd_process_device_init_vm error handling

## Summary
Severity: High
Advisory: CVE-2022-50354
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50354
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.0.19, >=6.1.0 <6.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix kfd_process_device_init_vm error handling

Should only destroy the ib_mem and let process cleanup worker to free
the outstanding BOs. Reset the pointer in pdd->qpd structure, to avoid
NULL pointer access in process destroy worker.

 BUG: kernel NULL pointer dereference, address: 0000000000000010
 Call Trace:
  amdgpu_amdkfd_gpuvm_unmap_gtt_bo_from_kernel+0x46/0xb0 [amdgpu]
  kfd_process_device_destroy_cwsr_dgpu+0x40/0x70 [amdgpu]
  kfd_process_destroy_pdds+0x71/0x190 [amdgpu]
  kfd_process_wq_release+0x2a2/0x3b0 [amdgpu]
  process_one_work+0x2a1/0x600
  worker_thread+0x39/0x3d0

## References
- https://git.kernel.org/stable/c/29d48b87db64b6697ddad007548e51d032081c59
- https://git.kernel.org/stable/c/9d74d1f52e16d8e07f7fbe52e96d6391418a2fe9
- https://git.kernel.org/stable/c/b6e78bd3bf2eb964c95eb2596d3cd367307a20b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50354.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50354
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
