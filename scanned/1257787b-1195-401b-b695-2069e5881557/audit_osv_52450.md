# [M] CVE-2021-47461

## Summary
Severity: Medium
Advisory: CVE-2021-47461
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47461
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

userfaultfd: fix a race between writeprotect and exit_mmap()

A race is possible when a process exits, its VMAs are removed by
exit_mmap() and at the same time userfaultfd_writeprotect() is called.

The race was detected by KASAN on a development kernel, but it appears
to be possible on vanilla kernels as well.

Use mmget_not_zero() to prevent the race as done in other userfaultfd
operations.

## References
- https://git.kernel.org/stable/c/149958ecd0627a9f1e9c678c25c665400054cd6a
- https://git.kernel.org/stable/c/3cda4bfffd4f755645577aaa9e96a606657b4525
- https://git.kernel.org/stable/c/cb185d5f1ebf900f4ae3bf84cee212e6dd035aca
