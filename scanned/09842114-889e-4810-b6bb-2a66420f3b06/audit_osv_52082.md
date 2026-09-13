# [M] CVE-2021-47051

## Summary
Severity: Medium
Advisory: CVE-2021-47051
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47051
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: fsl-lpspi: Fix PM reference leak in lpspi_prepare_xfer_hardware()

pm_runtime_get_sync will increment pm usage counter even it failed.
Forgetting to putting operation will result in reference leak here.
Fix it by replacing it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/b8207bfc539cd07d15e753ff2d179c5b61c673b1
- https://git.kernel.org/stable/c/ce02e58ddf8658a4c3bed2296f32a5873b3f7cce
- https://git.kernel.org/stable/c/4a01ad002d2e03c399af536562693752af7c81b1
- https://git.kernel.org/stable/c/6a2b5cee0d31ab6cc51030c441135b0e31217282
- https://git.kernel.org/stable/c/a03675497970a93fcf25d81d9d92a59c2d7377a7
