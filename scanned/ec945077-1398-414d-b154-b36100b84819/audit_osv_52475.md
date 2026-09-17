# [M] CVE-2021-47490

## Summary
Severity: Medium
Advisory: CVE-2021-47490
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47490
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/ttm: fix memleak in ttm_transfered_destroy

We need to cleanup the fences for ghost objects as well.

Bug: https://bugzilla.kernel.org/show_bug.cgi?id=214029
Bug: https://bugzilla.kernel.org/show_bug.cgi?id=214447

## References
- https://git.kernel.org/stable/c/bbc920fb320f1c241cc34ac85edaa0058922246a
- https://git.kernel.org/stable/c/bd99782f3ca491879e8524c89b1c0f40071903bd
- https://git.kernel.org/stable/c/c21b4002214c1c7e7b627b9b53375612f7aab6db
- https://git.kernel.org/stable/c/0db55f9a1bafbe3dac750ea669de9134922389b5
- https://git.kernel.org/stable/c/132a3d998d6753047f22152731fba2b0d6b463dd
- https://git.kernel.org/stable/c/960b1fdfc39aba8f41e9e27b2de0c925c74182d9
