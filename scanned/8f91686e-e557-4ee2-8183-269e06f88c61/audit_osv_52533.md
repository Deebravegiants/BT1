# [M] CVE-2021-47551

## Summary
Severity: Medium
Advisory: CVE-2021-47551
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47551
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/amdkfd: Fix kernel panic when reset failed and been triggered again

In SRIOV configuration, the reset may failed to bring asic back to normal but stop cpsch
already been called, the start_cpsch will not be called since there is no resume in this
case.  When reset been triggered again, driver should avoid to do uninitialization again.

## References
- https://git.kernel.org/stable/c/06c6f8f86ec243b89e52f0c3dc7062bcb9de74df
- https://git.kernel.org/stable/c/2cf49e00d40d5132e3d067b5aa6d84791929ab15
- https://git.kernel.org/stable/c/74aafe99efb68f15e50be9f7032c2168512f98a8
