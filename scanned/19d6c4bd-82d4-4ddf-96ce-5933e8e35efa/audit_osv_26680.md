# [H] drm/amdgpu: unmap and remove csa_va properly

## Summary
Severity: High
Advisory: CVE-2023-53545
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53545
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: unmap and remove csa_va properly

Root PD BO should be reserved before unmap and remove
a bo_va from VM otherwise lockdep will complain.

v2: check fpriv->csa_va is not NULL instead of amdgpu_mcbp (christian)

[14616.936827] WARNING: CPU: 6 PID: 1711 at drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c:1762 amdgpu_vm_bo_del+0x399/0x3f0 [amdgpu]
[14616.937096] Call Trace:
[14616.937097]  <TASK>
[14616.937102]  amdgpu_driver_postclose_kms+0x249/0x2f0 [amdgpu]
[14616.937187]  drm_file_free+0x1d6/0x300 [drm]
[14616.937207]  drm_close_helper.isra.0+0x62/0x70 [drm]
[14616.937220]  drm_release+0x5e/0x100 [drm]
[14616.937234]  __fput+0x9f/0x280
[14616.937239]  ____fput+0xe/0x20
[14616.937241]  task_work_run+0x61/0x90
[14616.937246]  exit_to_user_mode_prepare+0x215/0x220
[14616.937251]  syscall_exit_to_user_mode+0x2a/0x60
[14616.937254]  do_syscall_64+0x48/0x90
[14616.937257]  entry_SYSCALL_64_after_hwframe+0x63/0xcd

## References
- https://git.kernel.org/stable/c/1bc35e637a81dac5f5155e83a277c26708c4d4d7
- https://git.kernel.org/stable/c/5daff15cd013422bc6d1efcfe82b586800025384
- https://git.kernel.org/stable/c/a3a96bf843c356d1d9b2d7f6d0784b6ee28ca9d0
- https://git.kernel.org/stable/c/ae325b245208394279a1dc412c831ebd71befb0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53545.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
