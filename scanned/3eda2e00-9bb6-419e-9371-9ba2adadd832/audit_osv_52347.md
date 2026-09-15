# [C] CVE-2021-47354

## Summary
Severity: Critical
Advisory: CVE-2021-47354
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47354
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sched: Avoid data corruptions

Wait for all dependencies of a job  to complete before
killing it to avoid data corruptions.

## References
- https://git.kernel.org/stable/c/c32d0f0e164ffab2a56c7cf8e612584b4b740e2e
- https://git.kernel.org/stable/c/0687411e2a8858262de2fc4a1d576016fd77292e
- https://git.kernel.org/stable/c/0b10ab80695d61422337ede6ff496552d8ace99d
- https://git.kernel.org/stable/c/50d7e03ad487cc45fc85164a299b945a41756ac0
- https://git.kernel.org/stable/c/a8e23e3c1ff9ec598ab1b3a941ace6045027781f
