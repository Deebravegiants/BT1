# [M] CVE-2021-47447

## Summary
Severity: Medium
Advisory: CVE-2021-47447
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47447
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/a3xx: fix error handling in a3xx_gpu_init()

These error paths returned 1 on failure, instead of a negative error
code.  This would lead to an Oops in the caller.  A second problem is
that the check for "if (ret != -ENODATA)" did not work because "ret" was
set to 1.

## References
- https://git.kernel.org/stable/c/3eda901995371d390ef82d0b6462f4ea8efbcfdf
- https://git.kernel.org/stable/c/d59e44e7821a8f2bb6f2e846b9167397a5f01608
