# [M] CVE-2021-46962

## Summary
Severity: Medium
Advisory: CVE-2021-46962
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46962
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mmc: uniphier-sd: Fix a resource leak in the remove function

A 'tmio_mmc_host_free()' call is missing in the remove function, in order
to balance a 'tmio_mmc_host_alloc()' call in the probe.
This is done in the error handling path of the probe, but not in the remove
function.

Add the missing call.

## References
- https://git.kernel.org/stable/c/d6e7fda496978f2763413b5523557b38dc2bf6c2
- https://git.kernel.org/stable/c/e29c84857e2d51aa017ce04284b962742fb97d9e
- https://git.kernel.org/stable/c/ebe0f12cf4c044f812c6d17011531582f9ac8bb3
- https://git.kernel.org/stable/c/0d8941b9b2d3e7b3481fdf43b1a6189d162175b7
- https://git.kernel.org/stable/c/25ac6ce65f1ab458982d15ec1caf441acd37106a
