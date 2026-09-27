# [M] drm/amdgpu: fix amdgpu_irq_put call trace in gmc_v11_0_hw_fini

## Summary
Severity: Medium
Advisory: CVE-2023-53237
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53237
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix amdgpu_irq_put call trace in gmc_v11_0_hw_fini

The gmc.ecc_irq is enabled by firmware per IFWI setting,
and the host driver is not privileged to enable/disable
the interrupt. So, it is meaningless to use the amdgpu_irq_put
function in gmc_v11_0_hw_fini, which also leads to the call
trace.

[  102.980303] Call Trace:
[  102.980303]  <TASK>
[  102.980304]  gmc_v11_0_hw_fini+0x54/0x90 [amdgpu]
[  102.980357]  gmc_v11_0_suspend+0xe/0x20 [amdgpu]
[  102.980409]  amdgpu_device_ip_suspend_phase2+0x240/0x460 [amdgpu]
[  102.980459]  amdgpu_device_ip_suspend+0x3d/0x80 [amdgpu]
[  102.980520]  amdgpu_device_pre_asic_reset+0xd9/0x490 [amdgpu]
[  102.980573]  amdgpu_device_gpu_recover.cold+0x548/0xce6 [amdgpu]
[  102.980687]  amdgpu_debugfs_reset_work+0x4c/0x70 [amdgpu]
[  102.980740]  process_one_work+0x21f/0x3f0
[  102.980741]  worker_thread+0x200/0x3e0
[  102.980742]  ? process_one_work+0x3f0/0x3f0
[  102.980743]  kthread+0xfd/0x130
[  102.980743]  ? kthread_complete_and_exit+0x20/0x20
[  102.980744]  ret_from_fork+0x22/0x30

## References
- https://git.kernel.org/stable/c/02e6cb9b3aeffc6b0e3955f6e0346293e2415cbc
- https://git.kernel.org/stable/c/13af556104fa93b1945c70bbf8a0a62cd2c92879
- https://git.kernel.org/stable/c/396401bc035ff5bf0c7b29c67caa10040eb3fb62
- https://git.kernel.org/stable/c/79038b78af931908d6f5d4e279d3afe32e7c840b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53237.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53237
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
