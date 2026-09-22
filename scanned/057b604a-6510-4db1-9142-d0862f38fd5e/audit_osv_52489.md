# [M] CVE-2021-47504

## Summary
Severity: Medium
Advisory: CVE-2021-47504
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47504
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: ensure task_work gets run as part of cancelations

If we successfully cancel a work item but that work item needs to be
processed through task_work, then we can be sleeping uninterruptibly
in io_uring_cancel_generic() and never process it. Hence we don't
make forward progress and we end up with an uninterruptible sleep
warning.

While in there, correct a comment that should be IFF, not IIF.

## References
- https://git.kernel.org/stable/c/78a780602075d8b00c98070fa26e389b3b3efa72
- https://git.kernel.org/stable/c/8e12976c0c19ebc14b60046b1348c516a74c25a2
