# [M] CVE-2021-47652

## Summary
Severity: Medium
Advisory: CVE-2021-47652
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47652
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

video: fbdev: smscufx: Fix null-ptr-deref in ufx_usb_probe()

I got a null-ptr-deref report:

BUG: kernel NULL pointer dereference, address: 0000000000000000
...
RIP: 0010:fb_destroy_modelist+0x38/0x100
...
Call Trace:
 ufx_usb_probe.cold+0x2b5/0xac1 [smscufx]
 usb_probe_interface+0x1aa/0x3c0 [usbcore]
 really_probe+0x167/0x460
...
 ret_from_fork+0x1f/0x30

If fb_alloc_cmap() fails in ufx_usb_probe(), fb_destroy_modelist() will
be called to destroy modelist in the error handling path. But modelist
has not been initialized yet, so it will result in null-ptr-deref.

Initialize modelist before calling fb_alloc_cmap() to fix this bug.

## References
- https://git.kernel.org/stable/c/d1b6a1f0c23b7164250479bf92e2893291dca539
- https://git.kernel.org/stable/c/da8b269cc0a2526ebeaccbe2484c999eb0f822cf
- https://git.kernel.org/stable/c/dd3a6cc7385b89ec2303f39dfc3bafa4e24cec4b
- https://git.kernel.org/stable/c/1791f487f877a9e83d81c8677bd3e7b259e7cb27
- https://git.kernel.org/stable/c/64ec3e678d76419f207b9cdd338dda438ca10b1c
- https://git.kernel.org/stable/c/c420b540db4b5d69de0a36d8b9d9a6a79a04f05a
- https://git.kernel.org/stable/c/d396c651e2b508b6179bb678cc029f3becbf5170
- https://git.kernel.org/stable/c/0fd28daec73525382e5c992db8743bf76e42cd5c
- https://git.kernel.org/stable/c/9280ef235b05e8f19f8bc6d547b992f0a0ef398d
