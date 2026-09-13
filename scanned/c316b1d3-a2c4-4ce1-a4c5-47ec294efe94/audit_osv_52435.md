# [M] CVE-2021-47446

## Summary
Severity: Medium
Advisory: CVE-2021-47446
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47446
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/a4xx: fix error handling in a4xx_gpu_init()

This code returns 1 on error instead of a negative error.  It leads to
an Oops in the caller.  A second problem is that the check for
"if (ret != -ENODATA)" cannot be true because "ret" is set to 1.

## References
- https://git.kernel.org/stable/c/3962d626eb3e3b23ebb2e2a61537fa764acbfe11
- https://git.kernel.org/stable/c/980d74e7d03ccf2eaa11d133416946bd880c7c08
