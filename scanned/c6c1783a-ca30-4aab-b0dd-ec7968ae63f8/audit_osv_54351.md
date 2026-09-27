# [H] CVE-2023-51043

## Summary
Severity: High
Advisory: CVE-2023-51043
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2023-51043
Type: osv

## Details
In the Linux kernel before 6.4.5, drivers/gpu/drm/drm_atomic.c has a use-after-free during a race condition between a nonblocking atomic commit and a driver unload.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.5
- https://github.com/torvalds/linux/commit/4e076c73e4f6e90816b30fcd4a0d7ab365087255
