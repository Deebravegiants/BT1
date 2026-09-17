# [M] CVE-2021-47478

## Summary
Severity: Medium
Advisory: CVE-2021-47478
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47478
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

isofs: Fix out of bound access for corrupted isofs image

When isofs image is suitably corrupted isofs_read_inode() can read data
beyond the end of buffer. Sanity-check the directory entry length before
using it.

## References
- https://git.kernel.org/stable/c/9ec33a9b8790c212cc926a88c5e2105f97f3f57e
- https://git.kernel.org/stable/c/afbd40f425227e661d991757e11cc4db024e761f
- https://git.kernel.org/stable/c/b0ddff8d68f2e43857a84dce54c3deab181c8ae1
- https://git.kernel.org/stable/c/b2fa1f52d22c5455217b294629346ad23a744945
- https://git.kernel.org/stable/c/e7fb722586a2936b37bdff096c095c30ca06404d
- https://git.kernel.org/stable/c/156ce5bb6cc43a80a743810199defb1dc3f55b7f
- https://git.kernel.org/stable/c/6e80e9314f8bb52d9eabe1907698718ff01120f5
- https://git.kernel.org/stable/c/86d4aedcbc69c0f84551fb70f953c24e396de2d7
- https://git.kernel.org/stable/c/e96a1866b40570b5950cda8602c2819189c62a48
