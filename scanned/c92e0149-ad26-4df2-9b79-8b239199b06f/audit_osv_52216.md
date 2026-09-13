# [M] CVE-2021-47205

## Summary
Severity: Medium
Advisory: CVE-2021-47205
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47205
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: sunxi-ng: Unregister clocks/resets when unbinding

Currently, unbinding a CCU driver unmaps the device's MMIO region, while
leaving its clocks/resets and their providers registered. This can cause
a page fault later when some clock operation tries to perform MMIO. Fix
this by separating the CCU initialization from the memory allocation,
and then using a devres callback to unregister the clocks and resets.

This also fixes a memory leak of the `struct ccu_reset`, and uses the
correct owner (the specific platform driver) for the clocks and resets.

Early OF clock providers are never unregistered, and limited error
handling is possible, so they are mostly unchanged. The error reporting
is made more consistent by moving the message inside of_sunxi_ccu_probe.

## References
- https://git.kernel.org/stable/c/9bec2b9c6134052994115d2d3374e96f2ccb9b9d
- https://git.kernel.org/stable/c/b5dd513daa70ee8f6d281a20bd28485ee9bb7db2
