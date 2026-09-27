# [H] CVE-2021-46993

## Summary
Severity: High
Advisory: CVE-2021-46993
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46993
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched: Fix out-of-bound access in uclamp

Util-clamp places tasks in different buckets based on their clamp values
for performance reasons. However, the size of buckets is currently
computed using a rounding division, which can lead to an off-by-one
error in some configurations.

For instance, with 20 buckets, the bucket size will be 1024/20=51. A
task with a clamp of 1024 will be mapped to bucket id 1024/51=20. Sadly,
correct indexes are in range [0,19], hence leading to an out of bound
memory access.

Clamp the bucket id to fix the issue.

## References
- https://git.kernel.org/stable/c/f7347c85490b92dd144fa1fba9e1eca501656ab3
- https://git.kernel.org/stable/c/3da3f804b82a0a382d523a21acf4cf3bb35f936d
- https://git.kernel.org/stable/c/42ee47c7e3569d9a0e2cb5053c496d97d380472f
- https://git.kernel.org/stable/c/687f523c134b7f0bd040ee1230f6d17990d54172
- https://git.kernel.org/stable/c/6d2f8909a5fabb73fe2a63918117943986c39b6c
