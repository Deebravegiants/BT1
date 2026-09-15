# [H] fbdev: hyperv_fb: Allow graceful removal of framebuffer

## Summary
Severity: High
Advisory: CVE-2025-21976
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21976
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: hyperv_fb: Allow graceful removal of framebuffer

When a Hyper-V framebuffer device is unbind, hyperv_fb driver tries to
release the framebuffer forcefully. If this framebuffer is in use it
produce the following WARN and hence this framebuffer is never released.

[   44.111220] WARNING: CPU: 35 PID: 1882 at drivers/video/fbdev/core/fb_info.c:70 framebuffer_release+0x2c/0x40
< snip >
[   44.111289] Call Trace:
[   44.111290]  <TASK>
[   44.111291]  ? show_regs+0x6c/0x80
[   44.111295]  ? __warn+0x8d/0x150
[   44.111298]  ? framebuffer_release+0x2c/0x40
[   44.111300]  ? report_bug+0x182/0x1b0
[   44.111303]  ? handle_bug+0x6e/0xb0
[   44.111306]  ? exc_invalid_op+0x18/0x80
[   44.111308]  ? asm_exc_invalid_op+0x1b/0x20
[   44.111311]  ? framebuffer_release+0x2c/0x40
[   44.111313]  ? hvfb_remove+0x86/0xa0 [hyperv_fb]
[   44.111315]  vmbus_remove+0x24/0x40 [hv_vmbus]
[   44.111323]  device_remove+0x40/0x80
[   44.111325]  device_release_driver_internal+0x20b/0x270
[   44.111327]  ? bus_find_device+0xb3/0xf0

Fix this by moving the release of framebuffer and assosiated memory
to fb_ops.fb_destroy function, so that framebuffer framework handles
it gracefully.

While we fix this, also replace manual registrations/unregistration of
framebuffer with devm_register_framebuffer.

## References
- https://git.kernel.org/stable/c/4545e2aa121aea304d33903099c03e29ed4fe50a
- https://git.kernel.org/stable/c/a7b583dc99c6cf4a96877017be1d08247e1ef2c7
- https://git.kernel.org/stable/c/ea2f45ab0e53b255f72c85ccd99e2b394fc5fceb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21976.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21976
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
