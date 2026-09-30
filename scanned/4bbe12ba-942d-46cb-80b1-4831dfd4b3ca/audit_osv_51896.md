# [H] CVE-2021-4460

## Summary
Severity: High
Advisory: CVE-2021-4460
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2021-4460
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix UBSAN shift-out-of-bounds warning

If get_num_sdma_queues or get_num_xgmi_sdma_queues is 0, we end up
doing a shift operation where the number of bits shifted equals
number of bits in the operand. This behaviour is undefined.

Set num_sdma_queues or num_xgmi_sdma_queues to ULLONG_MAX, if the
count is >= number of bits in the operand.

Bug: https://gitlab.freedesktop.org/drm/amd/-/issues/1472

## References
- https://git.kernel.org/stable/c/1874b0ef1426b873de94c61861e38f29a8df714c
- https://git.kernel.org/stable/c/3fdc5182700910a685d23df57d65166e8556a266
- https://git.kernel.org/stable/c/50e2fc36e72d4ad672032ebf646cecb48656efe0
- https://git.kernel.org/stable/c/9069b1b542de8f3bbffef868aff41521b21485cf
- https://git.kernel.org/stable/c/0c0356ef2498c1a250fe3846f30293f828737309
