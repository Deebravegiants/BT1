# [M] CVE-2021-47165

## Summary
Severity: Medium
Advisory: CVE-2021-47165
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47165
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/meson: fix shutdown crash when component not probed

When main component is not probed, by example when the dw-hdmi module is
not loaded yet or in probe defer, the following crash appears on shutdown:

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000038
...
pc : meson_drv_shutdown+0x24/0x50
lr : platform_drv_shutdown+0x20/0x30
...
Call trace:
meson_drv_shutdown+0x24/0x50
platform_drv_shutdown+0x20/0x30
device_shutdown+0x158/0x360
kernel_restart_prepare+0x38/0x48
kernel_restart+0x18/0x68
__do_sys_reboot+0x224/0x250
__arm64_sys_reboot+0x24/0x30
...

Simply check if the priv struct has been allocated before using it.

## References
- https://git.kernel.org/stable/c/b4298d33c1fcce511ffe84d8d3de07e220300f9b
- https://git.kernel.org/stable/c/b4b91033a0b11fe9ade58156cd9168f89f4a8c1a
- https://git.kernel.org/stable/c/d66083c0d6f5125a4d982aa177dd71ab4cd3d212
- https://git.kernel.org/stable/c/e256a0eb43e17209e347409a80805b1659398d68
- https://git.kernel.org/stable/c/4ce2bf20b4a6e307e114847d60b2bf40a6a1fac0
- https://git.kernel.org/stable/c/7cfc4ea78fc103ea51ecbacd9236abb5b1c490d2
