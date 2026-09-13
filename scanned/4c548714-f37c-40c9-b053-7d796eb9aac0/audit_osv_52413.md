# [M] CVE-2021-47422

## Summary
Severity: Medium
Advisory: CVE-2021-47422
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47422
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/nouveau/kms/nv50-: fix file release memory leak

When using single_open() for opening, single_release() should be
called, otherwise the 'op' allocated in single_open() will be leaked.

## References
- https://git.kernel.org/stable/c/0b3d4945cc7e7ea1acd52cb06dfa83bfe265b6d5
- https://git.kernel.org/stable/c/0b4e9fc14973a94ac0520f19b3633493ae13c912
- https://git.kernel.org/stable/c/65fff0a8efcdca8d84ffe3e23057c3b32403482d
