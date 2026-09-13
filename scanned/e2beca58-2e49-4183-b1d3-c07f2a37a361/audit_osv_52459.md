# [M] CVE-2021-47471

## Summary
Severity: Medium
Advisory: CVE-2021-47471
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47471
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: mxsfb: Fix NULL pointer dereference crash on unload

The mxsfb->crtc.funcs may already be NULL when unloading the driver,
in which case calling mxsfb_irq_disable() via drm_irq_uninstall() from
mxsfb_unload() leads to NULL pointer dereference.

Since all we care about is masking the IRQ and mxsfb->base is still
valid, just use that to clear and mask the IRQ.

## References
- https://git.kernel.org/stable/c/3cfc183052c3dbf8eae57b6c1685dab00ed3db4a
- https://git.kernel.org/stable/c/b0e6db0656ddfd8bb57303c2ef61ee1c1cc694a8
- https://git.kernel.org/stable/c/f40c2281d2c0674d32ba732fee45222d76495472
