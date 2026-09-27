# [M] drm/msm/disp/dpu1: avoid clearing hw interrupts if hw_intr is null during drm uninit

## Summary
Severity: Medium
Advisory: CVE-2022-49483
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49483
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/disp/dpu1: avoid clearing hw interrupts if hw_intr is null during drm uninit

If edp modeset init is failed due to panel being not ready and
probe defers during drm bind, avoid clearing irqs and dereference
hw_intr when hw_intr is null.

BUG: Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000

Call trace:
 dpu_core_irq_uninstall+0x50/0xb0
 dpu_irq_uninstall+0x18/0x24
 msm_drm_uninit+0xd8/0x16c
 msm_drm_bind+0x580/0x5fc
 try_to_bring_up_master+0x168/0x1c0
 __component_add+0xb4/0x178
 component_add+0x1c/0x28
 dp_display_probe+0x38c/0x400
 platform_probe+0xb0/0xd0
 really_probe+0xcc/0x2c8
 __driver_probe_device+0xbc/0xe8
 driver_probe_device+0x48/0xf0
 __device_attach_driver+0xa0/0xc8
 bus_for_each_drv+0x8c/0xd8
 __device_attach+0xc4/0x150
 device_initial_probe+0x1c/0x28

Changes in V2:
- Update commit message and coreect fixes tag.

Patchwork: https://patchwork.freedesktop.org/patch/484430/

## References
- https://git.kernel.org/stable/c/01013ba9bbddc62f7d011163cebfd7ed06bb698b
- https://git.kernel.org/stable/c/a7ca30c3a8b2e8bda65f2b922d382ac056be8aa4
- https://git.kernel.org/stable/c/a800701429313149afde18d98821554fbfcb3164
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49483.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49483
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
