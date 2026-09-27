# [M] CVE-2021-47530

## Summary
Severity: Medium
Advisory: CVE-2021-47530
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47530
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix wait_fence submitqueue leak

We weren't dropping the submitqueue reference in all paths.  In
particular, when the fence has already been signalled. Split out
a helper to simplify handling this in the various different return
paths.

## References
- https://git.kernel.org/stable/c/4c3cdbf2540319ea674f1f3c54f31f14c6f39647
- https://git.kernel.org/stable/c/ea0006d390a28012f8187717aea61498b2b341e5
