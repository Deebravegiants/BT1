# [M] CVE-2021-46994

## Summary
Severity: Medium
Advisory: CVE-2021-46994
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46994
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: mcp251x: fix resume from sleep before interface was brought up

Since 8ce8c0abcba3 the driver queues work via priv->restart_work when
resuming after suspend, even when the interface was not previously
enabled. This causes a null dereference error as the workqueue is only
allocated and initialized in mcp251x_open().

To fix this we move the workqueue init to mcp251x_can_probe() as there
is no reason to do it later and repeat it whenever mcp251x_open() is
called.

[mkl: fix error handling in mcp251x_stop()]

## References
- https://git.kernel.org/stable/c/03c427147b2d3e503af258711af4fc792b89b0af
- https://git.kernel.org/stable/c/6f8f1c27b577de15f69fefce3c502bb6300d825c
- https://git.kernel.org/stable/c/e1e10a390fd9479209c4d834d916ca5e6d5d396b
- https://git.kernel.org/stable/c/eecb4df8ec9f896b19ee05bfa632ac6c1dcd8f21
