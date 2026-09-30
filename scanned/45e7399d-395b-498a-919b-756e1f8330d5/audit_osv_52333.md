# [M] CVE-2021-47339

## Summary
Severity: Medium
Advisory: CVE-2021-47339
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47339
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: v4l2-core: explicitly clear ioctl input data

As seen from a recent syzbot bug report, mistakes in the compat ioctl
implementation can lead to uninitialized kernel stack data getting used
as input for driver ioctl handlers.

The reported bug is now fixed, but it's possible that other related
bugs are still present or get added in the future. As the drivers need
to check user input already, the possible impact is fairly low, but it
might still cause an information leak.

To be on the safe side, always clear the entire ioctl buffer before
calling the conversion handler functions that are meant to initialize
them.

## References
- https://git.kernel.org/stable/c/dc02c0b2bd6096f2f3ce63e1fc317aeda05f74d8
- https://git.kernel.org/stable/c/7b53cca764f9b291b7907fcd39d9e66ad728ee0b
- https://git.kernel.org/stable/c/bfb48b54db25c3b4ef4bef5e0691464ebc4aa335
